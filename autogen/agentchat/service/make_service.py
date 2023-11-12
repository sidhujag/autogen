from .. import GroupChatManager
from ..contrib.gpt_assistant_agent import GPTAssistantAgent

class MakeService:
    
    AGENT_REGISTRY: dict[str, GPTAssistantAgent] = {}
    GROUP_REGISTRY: dict[str, GroupChatManager] = {}
    @staticmethod
    def get_service(service_type):
        from . import AgentService, FunctionsService, GroupService
        if service_type == 'agent':
            return AgentService()
        elif service_type == 'function':
            return FunctionsService()
        elif service_type == 'group':
            return GroupService()

    @staticmethod
    def _get_short_description(full_description: str) -> str:
        return (full_description[:75] + '...') if len(full_description) > 75 else full_description
