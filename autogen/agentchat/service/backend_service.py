
import requests
import json
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Tuple, Dict

AUTOGEN_BACKEND = "127.0.0.1:8001"

class AuthAgent(BaseModel):
    api_key: str
    namespace_id: str

class DeleteAgentModel(BaseModel):
    name: str
    auth: AuthAgent
    
class GetAgentModel(BaseModel):
    name: str
    auth: AuthAgent

class GetGroupModel(BaseModel):
    name: str
    auth: AuthAgent
    
class GetFunctionModel(BaseModel):
    name: str
    auth: AuthAgent
    
class DiscoverAgentsModel(BaseModel):
    query: str
    category: Optional[str] = None
    auth: AuthAgent

class DiscoverGroupsModel(BaseModel):
    query: str
    auth: AuthAgent
    
class DiscoverFunctionsModel(BaseModel):
    query: Optional[str] = None
    category: str
    auth: AuthAgent

class UpsertAgentModel(BaseModel):
    name: str
    auth: AuthAgent
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
    auth: AuthAgent
    description: Optional[str] = None
    agents_to_add: Optional[List[str]] = None
    agents_to_remove: Optional[List[str]] = None
      
class BaseAgent(BaseModel):
    name: str = Field(default="")
    auth: AuthAgent
    assistant_id: str = Field(default="")
    description: str = Field(default="")
    human_input_mode: str = Field(default="TERMINATE")
    default_auto_reply: str = Field(default="")
    system_message: str = Field(default="")
    category: str = Field(default="")
    capability: int = Field(default=1)
    files: Dict[str, str] = Field(default_factory=dict)
    
class BaseGroup(BaseModel):
    name: str = Field(default="")
    auth: AuthAgent
    description: str = Field(default="")
    agent_names: List[str] = Field(default_factory=list)
    outgoing: Dict[str, int] = Field(default_factory=dict)
    incoming: Dict[str, int] = Field(default_factory=dict)

class GroupInfo(BaseGroup):
    agents: Dict[str, Dict] = Field(default_factory=dict)

class AgentInfo(BaseModel):
    name: str
    description: str
    system_message: str
    capability: int
    files: Dict[str, str]

class BackendAgent(BaseAgent):
    functions: List[dict] = Field(default_factory=list)

class OpenAIParameter(BaseModel):
    type: str = "object"
    properties: dict[str, Any] = {}
    required: Optional[List[str]] = []

class AddFunctionModel(BaseModel):
    name: str
    auth: AuthAgent
    status: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    class_name: str = None
    parameters: OpenAIParameter = None
    function_code: Optional[str] = None
    last_updater: str = None

class BaseFunction(BaseModel):
    name: str = Field(default="")
    namespace_id: str = Field(default="")
    status: str = Field(default="")
    last_updater: str = Field(default="")
    description: str = Field(default="")
    parameters: OpenAIParameter = Field(default_factory=OpenAIParameter)
    category: str = Field(default="")
    function_code: str = Field(default="")
    class_name: str = Field(default="")
    
class UpdateComms(BaseModel):
    auth: AuthAgent
    sender: str
    receiver: str

class BackendService:
    @staticmethod
    def delete_backend_agents(data_models: List[DeleteAgentModel]):
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("delete_agents", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None

    @staticmethod
    def upsert_backend_agents(data_models: List[UpsertAgentModel]):
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("upsert_agents", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None
    
    @staticmethod
    def upsert_backend_groups(data_models: List[UpsertGroupModel]):
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("upsert_groups", list_of_dicts)
        if response != "success":
            return response
        if err is not None:
            return err
        return None
    
    @staticmethod
    def update_communication_stats(comms: UpdateComms):
        response, err = BackendService.call("update_communication_stats", comms.dict())
        if response != "success":
            return response
        if err is not None:
            return err
        return None

    @staticmethod
    def get_backend_agents(data_models: List[GetAgentModel]) -> Tuple[Optional[List[BackendAgent]], Optional[str]]:
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("get_agents", list_of_dicts)
        if err is not None:
            return None, err
        if not isinstance(response, list):
            return None, json.dumps({"error": "Unexpected response format: backend response is not a list"})
        return [BackendAgent(**agent) for agent in response], None

    @staticmethod
    def get_backend_groups(data_models: List[GetGroupModel]) -> Tuple[Optional[List[BaseGroup]], Optional[str]]:
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("get_groups", list_of_dicts)
        if err is not None:
            return None, err
        if not isinstance(response, list):
            return None, json.dumps({"error": "Unexpected response format: backend response is not a list"})
        return [BaseGroup(**agent) for agent in response], None

    @staticmethod
    def get_backend_functions(data_models: List[GetFunctionModel]) -> Tuple[Optional[List[BaseFunction]], Optional[str]]:
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("get_functions", list_of_dicts)
        if err is not None:
            return None, err
        if not isinstance(response, list):
            return None, json.dumps({"error": "Unexpected response format: backend response is not a list"})
        return [BaseFunction(**agent) for agent in response], None

    @staticmethod
    def upsert_backend_functions(list_data_model: List[AddFunctionModel]):
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
    def discover_backend_functions(data_model: DiscoverFunctionsModel):
        response, err = BackendService.call("discover_functions", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    @staticmethod
    def discover_backend_agents(data_model: DiscoverAgentsModel):
        response, err = BackendService.call("discover_agents", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    @staticmethod
    def discover_backend_groups(data_model: DiscoverGroupsModel):
        response, err = BackendService.call("discover_groups", data_model.dict(exclude_none=True))
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
        return None, json.dumps({"error": "invalid response"})