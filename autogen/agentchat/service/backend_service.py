
import requests
import json
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Tuple, Dict

AUTOGEN_BACKEND = "127.0.0.1:8001"

class AuthAgent(BaseModel):
    api_key: str = ''
    zapier_api_key: str = ''
    gh_pat: str = ''
    gh_user: str = ''
    namespace_id: str = ''

class DeleteAgentModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()

class DeleteGroupModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()

class DeleteCodeAssistantsModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()

class DeleteCodeRepositoryModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()

class GetAgentModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()

class GetGroupModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()
    
class GetFunctionModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()
    
class GetCodingAssistantModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()

class GetCodeRepositoryModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()
    
class DiscoverAgentsModel(BaseModel):
    query: str
    category: Optional[str] = None
    auth: AuthAgent = AuthAgent()

class DiscoverGroupsModel(BaseModel):
    query: str
    auth: AuthAgent = AuthAgent()
    
class DiscoverFunctionsModel(BaseModel):
    query: Optional[str] = None
    category: str
    auth: AuthAgent = AuthAgent()

class DiscoverCodingAssistantModel(BaseModel):
    query: str
    auth: AuthAgent = AuthAgent()

class DiscoverCodeRepositoryModel(BaseModel):
    query: str
    auth: AuthAgent = AuthAgent()
    
class UpsertAgentModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()
    assistant_id: Optional[str] = None
    human_input_mode: Optional[str] = None
    default_auto_reply: Optional[str] = None
    description: Optional[str] = None
    system_message: Optional[str] = None
    functions_to_add: Optional[List[str]] = None
    functions_to_remove: Optional[List[str]] = None
    category: Optional[str] = None
    capability: Optional[int] = None
    files_to_add: Optional[Dict[str, str]] = None
    files_to_remove: Optional[List[str]] = None

class UpsertGroupModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()
    description: Optional[str] = None
    agents_to_add: Optional[List[str]] = None
    agents_to_remove: Optional[List[str]] = None
    locked: Optional[bool] = None

class UpsertCodingAssistantModel(BaseModel):
    name: str
    repository_name: str
    auth: AuthAgent = AuthAgent()
    description: Optional[str] = None
    model: Optional[str] = None
    files: Optional[List[str]] = None
    show_diffs: Optional[bool] = None
    dry_run: Optional[bool] = None
    map_tokens: Optional[int] = None
    verbose: Optional[bool] = None

class UpsertCodeRepositoryModel(BaseModel):
    name: str
    auth: AuthAgent = AuthAgent()
    description: Optional[str] = None
    private: Optional[bool] = None
    gh_remote_url: Optional[str] = None
    upstream_gh_remote_url: Optional[str] = None
    associated_code_assistants: Optional[set[str]] = None

class BaseAgent(BaseModel):
    name: str = Field(default="")
    auth: AuthAgent = Field(default=AuthAgent)
    assistant_id: str = Field(default="")
    description: str = Field(default="")
    human_input_mode: str = Field(default="TERMINATE")
    default_auto_reply: str = Field(default="")
    system_message: str = Field(default="")
    category: str = Field(default="")
    capability: int = Field(default=0)
    files: Dict[str, str] = Field(default_factory=dict)
    function_names: List[str] = Field(default_factory=list)

class BaseGroup(BaseModel):
    name: str = Field(default="")
    auth: AuthAgent = Field(default=AuthAgent)
    description: str = Field(default="")
    agent_names: List[str] = Field(default_factory=list)
    outgoing: Dict[str, int] = Field(default_factory=dict)
    incoming: Dict[str, int] = Field(default_factory=dict)
    locked: Optional[bool] = Field(default=False)

class GroupInfo(BaseGroup):
    agents: Dict[str, Dict] = Field(default_factory=dict)

class FunctionInfo(BaseModel):
    name: str
    status: str

class AgentInfo(BaseModel):
    name: str
    description: str
    system_message: str
    capability: int
    files: Dict[str, str]
    functions: List[FunctionInfo]

class OpenAIParameter(BaseModel):
    type: str = "object"
    properties: dict[str, Any] = {}
    required: Optional[List[str]] = []

class BaseFunction(BaseModel):
    name: str = Field(default="")
    status: str = Field(default="")
    last_updater: str = Field(default="")
    description: str = Field(default="")
    parameters: OpenAIParameter = Field(default_factory=OpenAIParameter)
    category: str = Field(default="")
    function_code: str = Field(default="")
    class_name: str = Field(default="")

class BaseCodingAssistant(BaseModel):
    name: str = Field(default="")
    auth: AuthAgent = Field(default=AuthAgent)
    repository_name: str = Field(default="")
    description: str = Field(default="")
    model: str = Field(default="")
    files: List[str] = Field(default=[])
    show_diffs: bool = Field(default=False)
    dry_run: bool = Field(default=False)
    map_tokens: int = Field(default=1024)
    verbose: bool = Field(default=False)
        
class BaseCodeRepository(BaseModel):
    name: str = Field(default="")
    auth: AuthAgent = Field(default=AuthAgent)
    description: str = Field(default="")
    gh_remote_url: str = Field(default="")
    upstream_gh_remote_url: str = Field(default="")
    associated_code_assistants: set[str] = Field(default=set())
    private: bool = Field(default=False)

class CodeRepositoryInfo(BaseModel):
    name: str = Field(default="")
    description: str = Field(default="")
    gh_remote_url: str = Field(default="")
    upstream_gh_remote_url: str = Field(default="")
    associated_code_assistants: set[str] = Field(default=set())
    private: bool = Field(default=False)
    is_forked: bool = Field(default=False)

class CodingAssistantInfo(BaseModel):
    name: str = Field(default="")
    gh_user: str = Field(default="")
    description: str = Field(default="")
    model: str = Field(default="")
    git_dir: str = Field(default="")
    files: set[str] = Field(default=set())
    show_diffs: bool = Field(default=False)
    dry_run: bool = Field(default=False)
    map_tokens: int = Field(default=1024)
    verbose: bool = Field(default=False)
    repository_info: CodeRepositoryInfo = Field(default=CodeRepositoryInfo)

class AddFunctionModel(BaseFunction):
    auth: AuthAgent = Field(default=AuthAgent)
    
class UpdateComms(BaseModel):
    auth: AuthAgent = AuthAgent()
    sender: str
    receiver: str

class BackendService:
    @staticmethod
    def delete_backend_agents(data_models: List[DeleteAgentModel]):
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("delete_agents", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None

    @staticmethod
    def delete_backend_coding_assistants(data_models: List[DeleteCodeAssistantsModel]):
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("delete_code_assistants", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None
    
    @staticmethod
    def delete_backend_code_repositories(data_models: List[DeleteCodeRepositoryModel]):
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("delete_code_repositories", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None
    
    @staticmethod
    def delete_groups(data_models: List[DeleteGroupModel]):
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("delete_groups", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None

    @staticmethod
    def upsert_backend_agents(data_models: List[UpsertAgentModel]):
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("upsert_agents", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None
    
    @staticmethod
    def upsert_backend_groups(data_models: List[UpsertGroupModel]):
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("upsert_groups", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None
    
    @staticmethod
    def update_communication_stats(comms: UpdateComms):
        from . import MakeService
        comms.auth = MakeService.auth
        response, err = BackendService.call("update_communication_stats", comms.dict())
        if response != "success":
            return response
        if err is not None:
            return err
        return None

    @staticmethod
    def get_backend_agents(data_models: List[GetAgentModel]) -> Tuple[Optional[List[BaseAgent]], Optional[str]]:
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("get_agents", list_of_dicts)
        if err is not None:
            return None, err
        if not isinstance(response, list):
            return None, json.dumps({"error": "Unexpected response format: backend response is not a list"})
        return [BaseAgent(**agent) for agent in response], None

    @staticmethod
    def get_backend_groups(data_models: List[GetGroupModel]) -> Tuple[Optional[List[BaseGroup]], Optional[str]]:
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("get_groups", list_of_dicts)
        if err is not None:
            return None, err
        if not isinstance(response, list):
            return None, json.dumps({"error": "Unexpected response format: backend response is not a list"})
        return [BaseGroup(**agent) for agent in response], None

    @staticmethod
    def get_backend_coding_assistants(data_models: List[GetCodingAssistantModel]) -> Tuple[Optional[List[BaseCodingAssistant]], Optional[str]]:
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("get_coding_assistants", list_of_dicts)
        if err is not None:
            return None, err
        if not isinstance(response, list):
            return None, json.dumps({"error": "Unexpected response format: backend response is not a list"})
        return [BaseCodingAssistant(**assistant) for assistant in response], None

    @staticmethod
    def get_backend_code_repositories(data_models: List[GetCodeRepositoryModel]) -> Tuple[Optional[List[BaseCodeRepository]], Optional[str]]:
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("get_code_repositories", list_of_dicts)
        if err is not None:
            return None, err
        if not isinstance(response, list):
            return None, json.dumps({"error": "Unexpected response format: backend response is not a list"})
        return [BaseCodeRepository(**assistant) for assistant in response], None

    @staticmethod
    def get_backend_functions(data_models: List[GetFunctionModel]) -> Tuple[Optional[List[BaseFunction]], Optional[str]]:
        from . import MakeService
        for model in data_models:
            model.auth = MakeService.auth
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("get_functions", list_of_dicts)
        if err is not None:
            return None, err
        if not isinstance(response, list):
            return None, json.dumps({"error": "Unexpected response format: backend response is not a list"})
        return [BaseFunction(**agent) for agent in response], None

    @staticmethod
    def upsert_backend_functions(list_data_model: List[AddFunctionModel]):
        from . import MakeService
        for model in list_data_model:
            model.auth = MakeService.auth
        # Convert each AddFunctionModel object in the list to a dictionary
        list_of_dicts = [model.dict(exclude_none=True) for model in list_data_model]
        # Make the backend call with the list of dictionaries
        response, err = BackendService.call("upsert_functions", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None

    @staticmethod
    def upsert_backend_coding_assistants(list_data_model: List[UpsertCodingAssistantModel]):
        from . import MakeService
        for model in list_data_model:
            model.auth = MakeService.auth
        # Convert each object in the list to a dictionary
        list_of_dicts = [model.dict(exclude_none=True) for model in list_data_model]
        # Make the backend call with the list of dictionaries
        response, err = BackendService.call("upsert_coding_assistants", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None

    @staticmethod
    def upsert_backend_code_repositories(list_data_model: List[UpsertCodeRepositoryModel]):
        from . import MakeService
        for model in list_data_model:
            model.auth = MakeService.auth
        # Convert each object in the list to a dictionary
        list_of_dicts = [model.dict(exclude_none=True) for model in list_data_model]
        # Make the backend call with the list of dictionaries
        response, err = BackendService.call("upsert_code_repositories", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None
    
    @staticmethod
    def discover_backend_functions(data_model: DiscoverFunctionsModel):
        from . import MakeService
        data_model.auth = MakeService.auth
        response, err = BackendService.call("discover_functions", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    @staticmethod
    def discover_backend_agents(data_model: DiscoverAgentsModel):
        from . import MakeService
        data_model.auth = MakeService.auth
        response, err = BackendService.call("discover_agents", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    @staticmethod
    def discover_backend_groups(data_model: DiscoverGroupsModel):
        from . import MakeService
        data_model.auth = MakeService.auth
        response, err = BackendService.call("discover_groups", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    @staticmethod
    def discover_backend_coding_assistants(data_model: DiscoverCodingAssistantModel):
        from . import MakeService
        data_model.auth = MakeService.auth
        response, err = BackendService.call("discover_coding_assistants", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    @staticmethod
    def discover_backend_code_repositories(data_model: DiscoverCodeRepositoryModel):
        from . import MakeService
        data_model.auth = MakeService.auth
        response, err = BackendService.call("discover_code_repositories", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None
    
    @staticmethod
    def call(endpoint, json_input):   
        try:
            response = requests.post(
                url=f'http://{AUTOGEN_BACKEND}/{endpoint}/',
                json=json_input
            )
            response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
        except requests.HTTPError as e:
            return None, json.dumps({"error": f"Error making call: {str(e)}"})
        if response.status_code == 200:
            return response.json()["response"], None
        return None, json.dumps({"error": "invalid response"})from . import MakeService
        data_model.auth = MakeService.auth