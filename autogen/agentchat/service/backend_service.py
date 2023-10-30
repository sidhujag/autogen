
import requests
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Tuple

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

class DiscoverAgentsModel(BaseModel):
    query: Optional[str] = None
    category: str
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
    base_system_message: Optional[str] = None
    function_names: Optional[List[str]] = None # cumulative
    category: Optional[str] = None
    agents: Optional[dict[str, bool]] = None
    invitees: Optional[dict[str, bool]] = None
    
class BaseAgent(BaseModel):
    name: str = Field(default="")
    auth: AuthAgent
    description: str = Field(default="")
    human_input_mode: str = Field(default="TERMINATE")
    default_auto_reply: str = Field(default="")
    system_message: str = Field(default="")
    base_system_message: str = Field(default="")
    category: str = Field(default="")
    agents: dict = Field(default_factory=dict)
    invitees: dict = Field(default_factory=dict)

class BackendAgent(BaseAgent):
    functions: List[dict] = Field(default_factory=list)

class OpenAIParameter(BaseModel):
    type: str
    properties: dict[str, Any]
    required: Optional[List[str]] = None

class AddFunctionModel(BaseModel):
    name: str
    description: str
    category: str
    class_name: str
    parameters: OpenAIParameter
    auth: AuthAgent
    packages: Optional[List[str]] = None
    code: Optional[str] = None

class BackendService:
    @staticmethod
    def delete_backend_agent(data_model: DeleteAgentModel):
        response, err = BackendService.call("delete_agent", data_model.dict(exclude_none=True))
        if err != None:
            return err
        return None
    
    @staticmethod
    def upsert_backend_agent(data_model: UpsertAgentModel):
        response, err = BackendService.call("upsert_agent", data_model.dict(exclude_none=True))
        if err != None:
            return err
        return None

    @staticmethod
    def get_backend_agent(data_model: GetAgentModel) -> Tuple[Optional[BackendAgent], Optional[str]]:
        response, err = BackendService.call("get_agent", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        if not isinstance(response, dict):
            return None, "Unexpected response format: backend response is not a dictionary"
        return BackendAgent(**response), None

    @staticmethod
    def add_backend_function(data_model: AddFunctionModel):
        response, err = BackendService.call("add_function", data_model.dict(exclude_none=True))
        if err != None:
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