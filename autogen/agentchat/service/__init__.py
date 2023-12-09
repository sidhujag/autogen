from .agent_service import AgentService
from .search_engine_serper import WebSearchSerperWrapper
from .zapier_service import ZapierService
from .functions_service import FunctionsService
from .make_service import MakeService
from .coding_assistance_service import CodingAssistantService
from .group_service import GroupService, INFO, TERMINATE, OPENAI_CODE_INTERPRETER, CODING_ASSISTANCE, FUNCTION_CODER, OPENAI_RETRIEVAL, OPENAI_FILES, MANAGEMENT
from .backend_service import (
    BackendService,
    AuthAgent, 
    DeleteAgentModel, 
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
    CodingAssistantInfo,
    UpsertAgentModel,
    AddFunctionModel,
    OpenAIParameter,
    UpdateComms,
    UpsertGroupModel,
    UpsertCodingAssistantModel,
    GetGroupModel,
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
    "WebSearchSerperWrapper",
    "MakeService",
    "FunctionsService",
    "AgentInfo",
    "FunctionInfo",
    "BackendService",
    "MakeService",
    "AuthAgent",
    "DeleteAgentModel",
    "GetAgentModel",
    "DiscoverAgentsModel",
    "DiscoverFunctionsModel",
    "DiscoverCodingAssistantModel",
    "BaseFunction",
    "BaseCodingAssistant",
    "GetFunctionModel",
    "GetCodingAssistantModel",
    "CodingAssistantInfo",
    "UpsertAgentModel",
    "AddFunctionModel",
    "OpenAIParameter",
    "GroupService",
    "CodingAssistantService",
    "UpsertGroupModel",
    "UpsertCodingAssistantModel",
    "GetGroupModel",
    "GroupInfo",
    "DiscoverGroupsModel",
    "INFO",
    "TERMINATE",
    "OPENAI_CODE_INTERPRETER",
    "CODING_ASSISTANCE",
    "FUNCTION_CODER",
    "OPENAI_RETRIEVAL",
    "OPENAI_FILES",
    "MANAGEMENT",
    "ZapierService"
]
