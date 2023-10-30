import json
from . import GroupChatManager, ConversableAgent, BackendService, MakeService, DiscoverAgentsModel, UpsertAgentModel, GetAgentModel

class AgentService:
    @staticmethod
    def get_agent(agent_model: GetAgentModel) -> ConversableAgent:
        agent: ConversableAgent = MakeService.AGENT_REGISTRY.get(agent_model.name)
        if agent is None:
            backend_agent, err = BackendService.get_backend_agent(agent_model)
            if err is None:
                agent = MakeService.make_agent(backend_agent)
                MakeService.AGENT_REGISTRY[agent_model.name] = agent
        return agent

    @staticmethod
    def send_message(sender: ConversableAgent, message: str, recipient: str, request_reply: bool = False) -> str:
        if sender is None:
            return "Could not send message: sender not found"
        to_agent = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=recipient))
        if to_agent is None:
            return "Could not send message: recipient not found"
        if isinstance(to_agent, GroupChatManager):
            # group manager should get a response so he can delegate further
            request_reply = True
            if sender.name not in to_agent.agents:
                return "Could not send message: Trying to send to a group that you are not in"
        sender.send(message=message, recipient=to_agent, request_reply=request_reply, silent=True)
        return "Sent message!"

    @staticmethod
    def discover_agents(sender: ConversableAgent, category: str, query: str = None) -> str:
        if sender is None:
            return "Sender not found"
        response, err = BackendService.discover_backend_agents(DiscoverAgentsModel(auth=sender.auth, query=query,category=category))
        if err is not None:
            return f"Could not discover agents: {err}"
        return response

    @staticmethod
    def create_or_update_agent(sender: ConversableAgent, agent_name: str, agent_description: str = None, system_message: str = None, function_names: str = None, category: str = None) -> str: 
        if sender is None:
            return "Sender not found"
        try:
            json_fns = json.loads(function_names)
        except json.JSONDecodeError as e:
            return f"Error parsing JSON function names when trying to create or update agent: {e}"
        err = MakeService.upsert_agent(UpsertAgentModel(
            auth=sender.auth,
            name=agent_name,
            description=agent_description,
            system_message=system_message,
            function_names=json_fns,
            category=category
        ))
        if err is not None:
            return f"Could not create or update agent: {err}"
        return "Agent created or updated successfully"
