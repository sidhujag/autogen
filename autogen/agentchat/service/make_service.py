from .. import GroupChatManager
from ..contrib.gpt_assistant_agent import GPTAssistantAgent
from ..service.backend_service import BaseFunction, AuthAgent
from aider.coders import Coder
class MakeService:
    CODE_ASSISTANT_REGISTRY: dict[str, Coder] = {}
    AGENT_REGISTRY: dict[str, GPTAssistantAgent] = {}
    GROUP_REGISTRY: dict[str, GroupChatManager] = {}
    FUNCTION_REGISTRY: dict[str, BaseFunction] = {}
    auth: AuthAgent = None
    openai_client: object = None
    @staticmethod
    def get_service(service_type):
        from . import AgentService, FunctionsService, GroupService, CodingAssistantService
        if service_type == 'agent':
            return AgentService()
        elif service_type == 'function':
            return FunctionsService()
        elif service_type == 'group':
            return GroupService()
        elif service_type == 'coding_assistance':
            return CodingAssistantService()
        
    @staticmethod
    def _get_short_description(full_description: str) -> str:
        return (full_description[:640] + '...') if len(full_description) > 640 else full_description