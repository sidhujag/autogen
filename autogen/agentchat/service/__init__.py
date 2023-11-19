from .agent_service import AgentService
from .search_engine_serper import WebSearchSerperWrapper
from .functions_service import FunctionsService
from .make_service import MakeService
from .group_service import GroupService, INFO, CODE_INTERPRETER, RETRIEVAL, FILES, MANAGEMENT
from .backend_service import (
    BackendService,
    AuthAgent, 
    DeleteAgentModel, 
    GetAgentModel, 
    AgentInfo,
    FunctionInfo,
    DiscoverAgentsModel, 
    DiscoverFunctionsModel,
    BaseFunction,
    GetFunctionModel,
    UpsertAgentModel,
    AddFunctionModel,
    OpenAIParameter,
    UpdateComms,
    UpsertGroupModel,
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
    "BaseFunction",
    "GetFunctionModel",
    "UpsertAgentModel",
    "AddFunctionModel",
    "OpenAIParameter",
    "GroupService",
    "UpsertGroupModel",
    "GetGroupModel",
    "GroupInfo",
    "DiscoverGroupsModel",
    "INFO",
    "CODE_INTERPRETER",
    "RETRIEVAL",
    "FILES",
    "MANAGEMENT"
]
