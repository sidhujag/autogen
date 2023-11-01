from typing import List, Optional, Union
from .. import GroupChatManager, GroupChat, ConversableAgent
is_termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

class MakeService:
    AGENT_SYSTEM_MESSAGE: str = """ 
    You are an automated AI agent. Solve problems step-by-step. Each agent should add unique value to a group, although remaining solo is an option, albeit less discoverable.
    In group tasks, leverage a social connection between agents to help in solving problems. Build a hierarchy of agency with synergistic relationships.
    Be curious and explore general capabilities based on your surroundings:
    1. Messaging agents
    2. Finding/creating agents
    3. Forming groups, inviting others
    4. Finding/creating/adding functions

    You are capable of generating and executing simple Python code directly. Create and execute simple python within conversations when necessary, although specific python agents may handle complex tasks.

    To interact or ask the user a question use agent 'UserProxyAgent'.
    Respond with only 'TERMINATE' when you are done.

    Guidelines for Writing Python Code:
    - Python 3.9+
    - Follow PEP8 coding standards.
    - Ensure that your code is clear and readable. Use meaningful naming.
    - If a function results in an error during execution the creator should update the function with code that works.
    - If a function or module you need is not available, search for it, ask other agents or the user to help you find or create it.
    
    Agent/Function discovery:
    - There are pre-defined functions/agents that have been put into a database that are discoverable by you through semantic lookup (discover_functions/discover_agents)
    - Do not make up function calls that are not provided in your context. You must add them to get access to call them.
    """
    AGENT_REGISTRY: dict[str, ConversableAgent] = {}
    @staticmethod
    def get_service(service_type):
        from . import GroupService, AgentService, FunctionsService
        if service_type == 'group':
            return GroupService()
        elif service_type == 'agent':
            return AgentService()
        elif service_type == 'function':
            return FunctionsService()
    
    @staticmethod
    def is_group_chat_data(backend_agent):
        return len(backend_agent.agents) > 0

    @staticmethod
    def update_agent(agent: ConversableAgent, backend_agent):
        from . import FunctionsService, AddFunctionModel
        if MakeService.is_group_chat_data(backend_agent):
            agent.update_system_message(backend_agent.system_message)
            agent.groupchat.agents = backend_agent.agents
            agent.groupchat.invitees = backend_agent.invitees
            agent.description = backend_agent.description
        else:
            agent.update_system_message(backend_agent.system_message+MakeService.AGENT_SYSTEM_MESSAGE)
        for function in backend_agent.functions:
            FunctionsService.define_function_internal(agent, AddFunctionModel(**function, auth=agent.auth))
        MakeService.AGENT_REGISTRY[agent.name] = agent
    
    @staticmethod
    def _create_group_agent(backend_agent) -> GroupChatManager:
        groupchat = GroupChat(
            agents=backend_agent.agents,
            invitees=backend_agent.invitees
        )
        return GroupChatManager(
            groupchat=groupchat,
            name=backend_agent.name,
            human_input_mode=backend_agent.human_input_mode,
            default_auto_reply=backend_agent.default_auto_reply,
            system_message=backend_agent.system_message,
            is_termination_msg=is_termination_msg
        )
    @staticmethod
    def _create_agent(backend_agent) -> GroupChatManager:
        return ConversableAgent(
                name=backend_agent.name,
                human_input_mode=backend_agent.human_input_mode,
                default_auto_reply=backend_agent.default_auto_reply,
                system_message=backend_agent.system_message+MakeService.AGENT_SYSTEM_MESSAGE,
                is_termination_msg=is_termination_msg
            )
    @staticmethod
    def make_agent(backend_agent, llm_config: Optional[Union[dict, bool]] = None):
        from . import FunctionsService, AddFunctionModel
        if MakeService.is_group_chat_data(backend_agent):
            agent = MakeService._create_group_agent(backend_agent)
        else:
            agent = MakeService._create_agent(backend_agent)
        agent.auth = backend_agent.auth
        agent.description = backend_agent.description
        if agent.llm_config is False:
            agent.llm_config = agent.DEFAULT_CONFIG.copy()
        if llm_config:
            agent.llm_config.update(llm_config)
       
        agent.llm_config["api_key"] = agent.auth.api_key
        agent._code_execution_config = {"work_dir":agent.auth.namespace_id, "use_docker":"python:3"}
        for function in backend_agent.functions:
            FunctionsService.define_function_internal(agent, AddFunctionModel(**function, auth=agent.auth))
        MakeService.AGENT_REGISTRY[agent.name] = agent
        return agent
    
    @staticmethod
    def upsert_agents(upsert_models):
        from . import BackendService, GetAgentModel
        
        # Step 1: Upsert all agents in batch
        err = BackendService.upsert_backend_agents(upsert_models)
        if err:
            return None, err

        # Step 2: Retrieve all agents from backend in batch
        get_agent_models = [GetAgentModel(auth=model.auth, name=model.name) for model in upsert_models]
        backend_agents, err = BackendService.get_backend_agents(get_agent_models)
        if err:
            return None, err

        # Step 3: Update local agent registry
        successful_agents = []
        for backend_agent in backend_agents:
            agent = MakeService.AGENT_REGISTRY.get(backend_agent.name)
            if agent is None:
                agent = MakeService.make_agent(backend_agent)
            else:
                MakeService.update_agent(agent, backend_agent)
            successful_agents.append(agent)

        return successful_agents, None
