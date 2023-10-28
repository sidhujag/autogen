from .. import GroupChatManager, GroupChat, ConversableAgent, BackendService, FunctionsService, GroupService, AgentService
from backend_service import AuthAgent, GetAgentModel, UpsertAgentModel
from ..service.group_function_specs import group_function_specs
from typing import Dict, List
AGENT_SYSTEM_MESSAGE = """ Solve problems step-by-step using available functions. Organize autonomously via groups, discovering or creating agents and functions for new abilities. Each agent should add unique value to a group, although remaining solo is an option, albeit less discoverable.
In group tasks, message the group manager to maintain global context, enabling delegation to the next agent. Message across groups and users for task resolution or delegation, always responding to task initiators upon completion.
Invite agents to join groups if beneficial. Form new groups with distinct names and managers to efficiently manage context and address concerns during problem-solving.
Within a group, be aware of existing agents and the manager, but continue discovering useful agents. Explore your surroundings to answer queries, like messaging the right agent, forming new groups, or adding functions to enhance your capabilities. Create and execute simple code within conversations when necessary, although specific coding agents handle complex tasks.
There usually is an agent or function available for almost anything you want to do, but if not then define new functions for generic code that may be useful. Similarily, define new agents for generic roles that are missing.
Prioritize organization, robustness, and efficiency within groups. Build synergistic relationships with other agents. Communicate via a UserProxyAgent to interact with the user. Explore using provided functions and communication with other agents, forming hierarchical groups to manage context and delegate tasks efficiently. Respond with TERMINATE once all tasks are completed."""
termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

class MakeService:
    AGENT_REGISTRY: Dict[str, ConversableAgent] = {}
    def get_service(self, service_type):
        if service_type == 'group':
            return GroupService()
        elif service_type == 'agent':
            return AgentService()
        elif service_type == 'function':
            return FunctionsService()
    
    def is_group_chat_data(self, agents: List[Dict]):
        return len(agents) > 0

    def update_agent(self, agent: ConversableAgent, system_message: str, description: str, invitees: List[str], agents: List[Dict], functions: List[Dict]):
        agent.update_system_message(system_message)
        if self.is_group_chat_data(agents):
            agents_list = [{'name': agent['name'], 'description': agent['description']} for agent in agents]
            agent.groupchat.agents = agents_list
            agent.groupchat.invitees = invitees
            agent.description = description
        for function in functions:
            FunctionsService.define_function_internal(agent=agent, **function)
        return agent

    def create_new_agent(self, auth_agent: AuthAgent, name: str, system_message: str, description: str, invitees: List[str], agents: List[Dict], functions: List[Dict], llm_config: Dict = None):
        if self.is_group_chat_data(agents):
            agents_list = [{'name': agent['name'], 'description': agent['description']} for agent in agents]
            groupchat = GroupChat(
                agents=agents_list,
                invitees=invitees,
                messages=[]
            )
            agent = GroupChatManager(
                groupchat=groupchat,
                name=name,
                system_message=system_message + AGENT_SYSTEM_MESSAGE,
                termination_msg=termination_msg
            )
        else:
            agent = ConversableAgent(
                name=name,
                system_message=system_message + AGENT_SYSTEM_MESSAGE,
                termination_msg=termination_msg
            )
        auth: AuthAgent = BackendService.get_auth(name)
        if auth is None:
            if auth_agent:
                auth = BackendService.set_auth(auth_agent)
            else:
                print("No auth, agent has no way to authenticate against backend!")
                return None

        agent.description = description
        if agent.llm_config is False:
            agent.llm_config = agent.DEFAULT_CONFIG.copy()
        if llm_config:
            agent.llm_config.update(llm_config)
       
        agent.llm_config["api_key"] = auth.api_key
        agent.llm_config["functions"] = group_function_specs
        
        agent.register_function(function_map={
            "send_message": AgentService.send_message,
            "join_group": GroupService.join_group,
            "invite_to_group": GroupService.invite_to_group,
            "create_group": GroupService.create_group,
            "leave_group": GroupService.leave_group,
            "discover_agents": AgentService.discover_agents,
            "create_or_update_agent": AgentService.create_or_update_agent,
            "discover_functions": FunctionsService.discover_functions,
            "add_functions": FunctionsService.add_functions,
            "define_function": FunctionsService.define_function
        })
        agent._code_execution_config = {"work_dir":auth.namespace_id, "use_docker":"python:3"}
        for function in functions:
            FunctionsService.define_function_internal(agent=agent, **function)
        return agent
    
    def upsert_agent(self, sender: ConversableAgent, upsertModel: UpsertAgentModel):
        agent: ConversableAgent = MakeService.AGENT_REGISTRY.get(upsertModel["name"])
        response, err = BackendService.upsert_agent_data(sender, upsertModel)
        if err is not None:
            return None, err
        agent_data, err = BackendService.get_agent_data(sender, GetAgentModel(name=upsertModel["name"]))
        if err is not None:
            return None, err
        if agent is None:
            agent = self.create_new_agent(**agent_data)
        else:
            agent = self.update_agent(agent=agent, **agent_data)
        MakeService.AGENT_REGISTRY[agent_data["name"]] = agent
        return response, None