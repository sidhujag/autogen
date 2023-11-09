
import requests
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Tuple, Dict, TypedDict

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
    human_input_mode: Optional[str] = None
    default_auto_reply: Optional[str] = None
    description: Optional[str] = None
    system_message: Optional[str] = None
    functions_to_add: Optional[List[str]] = None
    functions_to_remove: Optional[List[str]] = None
    category: Optional[str] = None
    type: Optional[str] = None

class UpsertGroupModel(BaseModel):
    name: str
    auth: AuthAgent
    description: Optional[str] = None
    agents_to_add: Optional[List[str]] = None
    agents_to_remove: Optional[List[str]] = None
    
class BaseAgent(BaseModel):
    name: str = Field(default="")
    auth: AuthAgent
    description: str = Field(default="")
    human_input_mode: str = Field(default="TERMINATE")
    default_auto_reply: str = Field(default="")
    system_message: str = Field(default="")
    category: str = Field(default="")
    type: str = Field(default="BASIC")

class BaseGroup(BaseModel):
    name: str = Field(default="")
    auth: AuthAgent
    description: str = Field(default="")
    agent_names: List[str] = Field(default_factory=list)
    outgoing: Dict[str, int] = Field(default_factory=dict)
    incoming: Dict[str, int] = Field(default_factory=dict)

class BackendAgent(BaseAgent):
    functions: List[dict] = Field(default_factory=list)

class OpenAIParameter(BaseModel):
    type: str = "object"
    properties: dict[str, Any] = {}
    required: Optional[List[str]] = []

class AddFunctionModel(BaseModel):
    name: str
    description: str
    auth: AuthAgent
    category: str
    class_name: str = None
    parameters: OpenAIParameter = None
    function_code: Optional[str] = None

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
            return None, "Unexpected response format: backend response is not a list"
        return [BackendAgent(**agent) for agent in response], None

    @staticmethod
    def get_backend_groups(data_models: List[GetGroupModel]) -> Tuple[Optional[List[BaseGroup]], Optional[str]]:
        list_of_dicts = [model.dict(exclude_none=True) for model in data_models]
        response, err = BackendService.call("get_groups", list_of_dicts)
        if err is not None:
            return None, err
        if not isinstance(response, list):
            return None, "Unexpected response format: backend response is not a list"
        return [BaseGroup(**agent) for agent in response], None


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
    def call(endpoint, json):   
        try:
            response = requests.post(
                url=f'http://{AUTOGEN_BACKEND}/{endpoint}/',
                json=json
            )
            response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
        except requests.HTTPError as e:
            return None, f"Error making call: {e}"
        if response.status_code == 200:
            return response.json()["response"], None
        return None, "invalid response"