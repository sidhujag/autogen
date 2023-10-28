from .. import GroupChatManager, GroupChat, ConversableAgent, BackendService, FunctionsService, GroupService, AgentService
from backend_service import AuthAgent, GetAgentModel
from typing import Dict

class MakeService:
    AGENT_REGISTRY: Dict[str, ConversableAgent] = {}
    def get_service(self, service_type):
        if service_type == 'group':
            return GroupService()
        elif service_type == 'agent':
            return AgentService()
        elif service_type == 'function':
            return FunctionsService()
    
    def is_group_chat_data(self, agent_data):
        return 'invitees' in agent_data and 'agents' in agent_data and len(agent_data['agents']) > 0

    def update_agent(self, agent: ConversableAgent, agent_data):
        agent.description = agent_data['description']
        agent.update_system_message(agent_data['system_message'])
        if self.is_group_chat_data(agent_data):
            agents_list = [{'name': agent['name'], 'description': agent['description']} for agent in agent_data['agents']]
            agent.groupchat.agents = agents_list
            agent.groupchat.invitees = agent_data['invitees']
        return agent

    def create_new_agent(self, agent_data):
        description = agent_data['description']
        name = agent_data['name']
        system_message = agent_data['system_message']
        if self.is_group_chat_data(agent_data):
            agents_list = [{'name': agent['name'], 'description': agent['description']} for agent in agent_data['agents']]
            groupchat = GroupChat(
                agents=agents_list,
                invitees=agent_data['invitees'],
                messages=[]
            )
            agent = GroupChatManager(
                groupchat=groupchat,
                name=name,
                description=description,
                system_message=system_message
            )
        else:
            agent = ConversableAgent(
                name=name,
                description=description,
                system_message=system_message
            )

        auth: AuthAgent = BackendService.get_auth(name)
        if auth is None:
            if 'auth' in agent_data:
                auth = BackendService.set_auth(agent_data)
            else:
                print("No auth, agent has no way to authenticate against backend!")
                return None
    
        if agent.llm_config is False:
            agent.llm_config = agent.DEFAULT_CONFIG.copy()
        if 'llm_config' in agent_data:
            agent.llm_config.update(agent_data['llm_config'])
        else:
            agent.llm_config['api_key'] = auth.api_key
        
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
        return agent
    
    def upsert_agent(self, sender: ConversableAgent, agent_data):
        agent: ConversableAgent = MakeService.AGENT_REGISTRY.get(agent_data["name"])
        response, err = BackendService.upsert_agent_data(sender, agent_data)
        if err is not None:
            return None, err
        agent_data, err = BackendService.get_agent_data(sender, GetAgentModel(name=agent_data["name"]))
        if err is not None:
            return None, err
        if agent is None:
            agent = self.create_new_agent(agent_data)
        else:
            agent = self.update_agent(agent, agent_data)
        for fn in agent_data['functions']:
            FunctionsService.define_function_internal(agent, fn['name'], fn['description'], fn['arguments'], fn['code'], fn['required'], fn['packages'], fn['class_name'])
        MakeService.AGENT_REGISTRY[agent_data["name"]] = agent
        return response, None