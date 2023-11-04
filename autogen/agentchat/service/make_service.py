from typing import List, Optional, Union
from .. import GroupChatManager, GroupChat, ConversableAgent
is_termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

class MakeService:
    AGENT_SYSTEM_MESSAGE: str = """ 
    You are an automated AI agent. Focus on the request or problem. Solve problems step-by-step. Each agent should add unique value to a group, although remaining solo is an option, albeit less discoverable.
    In group tasks, leverage a social connection between agents to help in solving problems. Build a hierarchy of agency with synergistic relationships.
    Be curious and explore general capabilities based on your surroundings.
    You can write and execute code directly (Python and shell script). When code is useful to solve problem, write then if necessary add to function. Functions can be added to agents. Call the function name only within agent. Agents can have multiple functions for various things. Groups may have multiple agents for various things.
    Respond with only 'TERMINATE' when you are done.
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
    def is_group(backend_agent):
        return backend_agent.group

    @staticmethod
    def update_agent(agent: ConversableAgent, backend_agent):
        from . import FunctionsService, AddFunctionModel, AgentService, GetAgentModel
        if MakeService.is_group(backend_agent):
            agent_names = agent.groupchat.agent_names
            for agent_name in backend_agent.agents:
                if agent_name not in agent_names:
                    agent = AgentService.get_agent(GetAgentModel(auth=backend_agent.auth, name=agent_name))
                    if agent is None:
                        return None, f"Could not get agent {agent_name}"
                    agent.groupchat.agents.append(agent)
            agent.update_system_message(backend_agent.system_message)
            agent.description = backend_agent.description
        else:
            agent.update_system_message(backend_agent.system_message+MakeService.AGENT_SYSTEM_MESSAGE)
        for function in backend_agent.functions:
            FunctionsService.define_function_internal(agent, AddFunctionModel(**function, auth=agent.auth))
        MakeService.AGENT_REGISTRY[agent.name] = agent
    
    @staticmethod
    def _create_group_agent(backend_agent) -> GroupChatManager:
        from . import AgentService, GetAgentModel
        group_agents = []
        for agent_name in backend_agent.agents:
            agent = AgentService.get_agent(GetAgentModel(auth=backend_agent.auth, name=agent_name))
            if agent is None:
                return None, f"Could not get group agent {agent_name}"
            group_agents.append(agent)
        groupchat = GroupChat(
            agents=group_agents,
            messages=[],
            max_round=50
        )
        return GroupChatManager(
            groupchat=groupchat,
            name=backend_agent.name,
            human_input_mode=backend_agent.human_input_mode,
            default_auto_reply=backend_agent.default_auto_reply,
            system_message=backend_agent.system_message,
            is_termination_msg=is_termination_msg
        ), None
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
        if MakeService.is_group(backend_agent):
            agent, err = MakeService._create_group_agent(backend_agent)
            if err is not None:
                return None, err
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
        return agent, None
    
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
                agent, err = MakeService.make_agent(backend_agent)
                if err is not None:
                    return None, err
            else:
                MakeService.update_agent(agent, backend_agent)
            successful_agents.append(agent)

        return successful_agents, None
