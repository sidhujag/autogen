from typing import List, Optional, Union
from .. import GroupChatManager, GroupChat, ConversableAgent
is_termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

class MakeService:
    AGENT_SYSTEM_MESSAGE: str = """ Solve problems step-by-step using available functions. Organize autonomously via groups, discovering or creating agents and functions for new abilities. Each agent should add unique value to a group, although remaining solo is an option, albeit less discoverable.
    In group tasks, message the group manager to maintain global context, enabling delegation to the next agent. Message across groups and users for task resolution or delegation, always responding to task initiators upon completion.
    Invite agents to join groups if beneficial. Form new groups with distinct names and managers to efficiently manage context and address concerns during problem-solving.
    Within a group, be aware of existing agents and the manager, but continue discovering useful agents. Explore your surroundings to answer queries, like messaging the right agent, forming new groups, or adding functions to enhance your capabilities. Create and execute simple code within conversations when necessary, although specific coding agents handle complex tasks.
    There usually is an agent or function available for almost anything you want to do, but if not then define new functions for generic code that may be useful. Similarily, define new agents for generic roles that are missing.
    Prioritize organization, robustness, and efficiency within groups. Build synergistic relationships with other agents. Communicate via a UserProxyAgent to interact with the user. Explore using provided functions and communication with other agents, forming hierarchical groups to manage context and delegate tasks efficiently. Respond with TERMINATE once all tasks are completed."""
    GROUP_MANAGER_SYSTEM_MESSAGE: str = """ As a group manager, continuously message relevant agents in your group until satisfied with the results or awaiting responses. Delegate tasks to agents sequentially based on your plan, informing the initiating agent once all tasks are complete. Communication halts if you stop messaging until a human or another agent messages you. Note: All messages in a group are shared with every agent, increasing context window requirements and inferencing costs with more communication and content.""" + AGENT_SYSTEM_MESSAGE
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
    def is_group_chat_data(agents: List[dict]):
        return len(agents) > 0

    @staticmethod
    def update_agent(agent: ConversableAgent, backend_agent):
        from . import FunctionsService, AddFunctionModel
        if MakeService.is_group_chat_data(backend_agent.agents):
            agent.update_system_message(backend_agent.system_message+MakeService.GROUP_MANAGER_SYSTEM_MESSAGE)
            agent.groupchat.agents = backend_agent.agents
            agent.groupchat.invitees = backend_agent.invitees
            agent.description = backend_agent.description
        else:
            agent.update_system_message(backend_agent.system_message+MakeService.AGENT_SYSTEM_MESSAGE)
        for function in backend_agent.functions:
            FunctionsService.define_function_internal(agent, AddFunctionModel(**function, auth=agent.auth))
        MakeService.AGENT_REGISTRY[agent.name] = agent

    @staticmethod
    def make_agent(backend_agent, llm_config: Optional[Union[dict, bool]] = None):
        from . import FunctionsService, AddFunctionModel
        if MakeService.is_group_chat_data(backend_agent.agents):
            groupchat = GroupChat(
                agents=backend_agent.agents,
                invitees=backend_agent.invitees
            )
            agent = GroupChatManager(
                groupchat=groupchat,
                name=backend_agent.name,
                human_input_mode=backend_agent.human_input_mode,
                default_auto_reply=backend_agent.default_auto_reply,
                system_message=backend_agent.system_message+MakeService.GROUP_MANAGER_SYSTEM_MESSAGE,
                is_termination_msg=is_termination_msg
            )
        else:
            agent = ConversableAgent(
                name=backend_agent.name,
                human_input_mode=backend_agent.human_input_mode,
                default_auto_reply=backend_agent.default_auto_reply,
                system_message=backend_agent.system_message+MakeService.AGENT_SYSTEM_MESSAGE,
                is_termination_msg=is_termination_msg
            )
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
