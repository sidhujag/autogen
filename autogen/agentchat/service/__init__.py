from .agent_service import AgentService
from .zapier_service import ZapierService
from .web_researcher import WebSurf
from .code_assistant import CodeAssistantAgent
from .functions_service import FunctionsService
from .make_service import MakeService
from .coding_assistance_service import CodingAssistantService
from .coding_repository_service import CodeRepositoryService
from .group_service import GroupService, DISCOVERY, TERMINATE, OPENAI_CODE_INTERPRETER, OPENAI_RETRIEVAL, OPENAI_FILES, MANAGEMENT
from .backend_service import (
    BackendService,
    AuthAgent, 
    DeleteAgentModel,
    DeleteCodeAssistantsModel,
    GetAgentModel,
    AgentInfo,
    FunctionInfo,
    DiscoverAgentsModel, 
    DiscoverFunctionsModel,
    DiscoverCodingAssistantModel,
    BaseFunction,
    BaseCodingAssistant,
    GetFunctionModel,
    GetCodingAssistantModel,
    CodeAssistantInput,
    CodeRequestInput,
    CodeExecInput,
    WebResearchInput,
    GetCodeRepositoryModel,
    UpsertCodeRepositoryModel,
    BaseCodeRepository,
    DiscoverCodeRepositoryModel,
    DeleteCodeRepositoryModel,
    CodeRepositoryInfo,
    CodingAssistantInfo,
    UpsertAgentModel,
    OpenAIParameter,
    UpdateComms,
    UpsertGroupModel,
    UpsertCodingAssistantModel,
    GetGroupModel,
    DeleteGroupModel,
    GroupInfo,
    DiscoverGroupsModel
)
from enum import Enum


class SearchEngineType(Enum):
    SERPAPI_GOOGLE = "serpapi"
    SERPER_GOOGLE = "serper"
    DIRECT_GOOGLE = "google"
    DUCK_DUCK_GO = "ddg"
    CUSTOM_ENGINE = "custom"

__all__ = [
    "UpdateComms",
    "AgentService",
    "FunctionsService",
    "AgentInfo",
    "FunctionInfo",
    "BackendService",
    "MakeService",
    "AuthAgent",
    "DeleteAgentModel",
    "DeleteCodeAssistantsModel",
    "GetAgentModel",
    "DiscoverAgentsModel",
    "DiscoverFunctionsModel",
    "DiscoverCodingAssistantModel",
    "BaseFunction",
    "BaseCodingAssistant",
    "GetFunctionModel",
    "GetCodingAssistantModel",
    "CodeAssistantInput",
    "CodeRequestInput",
    "CodeExecInput",
    "WebResearchInput",
    "GetCodeRepositoryModel",
    "DiscoverCodeRepositoryModel",
    "UpsertCodeRepositoryModel",
    "BaseCodeRepository",
    "DeleteCodeRepositoryModel",
    "CodeRepositoryInfo",
    "CodingAssistantInfo",
    "UpsertAgentModel",
    "OpenAIParameter",
    "GroupService",
    "CodingAssistantService",
    "CodeRepositoryService",
    "UpsertGroupModel",
    "UpsertCodingAssistantModel",
    "GetGroupModel",
    "DeleteGroupModel",
    "GroupInfo",
    "DiscoverGroupsModel",
    "DISCOVERY",
    "TERMINATE",
    "OPENAI_CODE_INTERPRETER",
    "OPENAI_RETRIEVAL",
    "OPENAI_FILES",
    "MANAGEMENT",
    "ZapierService",
    "WebSurf",
    "CodeAssistantAgent"
]
