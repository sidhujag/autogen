import json
from .. import GroupChatManager, ConversableAgent, BackendService, MakeService
from backend_service import DiscoverAgentsModel, UpsertAgentModel

class AgentService:
    def get_agent(self, agent_name: str) -> ConversableAgent:
        agent: ConversableAgent = MakeService.AGENT_REGISTRY.get(agent_name)
        if agent is None:
            agent_data, err = BackendService.get_agent_data(agent_name)
            if err is None:
                agent = MakeService.create_new_agent(agent_data)
                MakeService.AGENT_REGISTRY[agent_name] = agent
        return agent

    def send_message(self, sender: ConversableAgent, message: str, recipient: str, request_reply: bool = False) -> str:
        if sender is None:
            return "Could not send message: sender not found"
        to_agent = self.get_agent(recipient)
        if to_agent == self:
            return "Could not send message: Trying to send to self"
        if isinstance(to_agent, GroupChatManager):
            # group manager should get a response so he can delegate further
            request_reply = True
            if to_agent.is_agent_in_group(self) is False:
                return "Could not send message: Trying to send to a group that you are not in"
        sender.send(message=message, recipient=to_agent, request_reply=request_reply, silent=True)
        return "Sent message!"

    def discover_agents(self, sender: ConversableAgent, category: str, query: str = None) -> str:
        if sender is None:
            return "Sender not found"
        response, err = BackendService.discover_agents(sender.name, DiscoverAgentsModel(query=query,category=category))
        if err is not None:
            return f"Could not discover agents: {err}"
        return response

    def create_or_update_agent(self, sender: ConversableAgent, agent_name: str, agent_description: str, system_message: str, function_names: str, category: str = None) -> str: 
        if sender is None:
            return "Sender not found"
        try:
            json_fns = json.loads(function_names)
        except json.JSONDecodeError as e:
            return f"Error parsing JSON function names when trying to create or update agent: {e}"
        response, err = MakeService.upsert_agent(UpsertAgentModel(
            name=agent_name,
            description=agent_description,
            system_message=system_message,
            function_names=json_fns,
            category=category
        ), sender)
        if err is not None:
            return f"Could not create or update agent: {err}"
        return "Agent created or updated successfully"
