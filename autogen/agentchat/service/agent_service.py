from .. import DiscoverableConversableAgent
from typing import List

class AgentService:
    @staticmethod
    def get_agent(agent_model) -> DiscoverableConversableAgent:
        from . import BackendService, MakeService
        agent: DiscoverableConversableAgent = MakeService.AGENT_REGISTRY.get(agent_model.name)
        if agent is None:
            backend_agent, err = BackendService.get_backend_agents([agent_model])
            if err is None:
                agent, err = MakeService.make_agent(backend_agent[0])
                if err is not None:
                    MakeService.AGENT_REGISTRY[agent_model.name] = agent
        return agent

    @staticmethod
    def send_message(sender: DiscoverableConversableAgent, message: str, recipient: str) -> str:
        from . import GetAgentModel
        if sender is None:
            return "Could not send message: sender not found"
        to_agent = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=recipient))
        if to_agent is None:
            return "Could not send message: recipient not found"

        sender.send(message=message, recipient=to_agent, request_reply=True, silent=False)

    @staticmethod
    def discover_agents(sender: DiscoverableConversableAgent, query: str, category: str = None) -> str:
        from . import BackendService, DiscoverAgentsModel
        if sender is None:
            return "Sender not found"
        response, err = BackendService.discover_backend_agents(DiscoverAgentsModel(auth=sender.auth, query=query,category=category))
        if err is not None:
            return f"Could not discover agents: {err}"
        return response

    @staticmethod
    def create_or_update_agent(sender: DiscoverableConversableAgent, name: str, description: str = None, system_message: str = None, functions_to_add: List[str] = None,  functions_to_remove: List[str] = None, category: str = None) -> str: 
        from . import MakeService, UpsertAgentModel
        if sender is None:
            return "Sender not found"
        agent, err = MakeService.upsert_agents([UpsertAgentModel(
            auth=sender.auth,
            name=name,
            description=description,
            system_message=system_message,
            functions_to_add=functions_to_add,
            functions_to_remove=functions_to_remove,
            category=category
        )])
        if err is not None:
            return f"Could not create or update agent: {err}"
        return "Agent created or updated!"
