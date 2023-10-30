
import requests
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from . import ConversableAgent

AUTOGEN_BACKEND = "127.0.0.1:8001"

class AuthAgent:
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
    function_names: Optional[List[str]] = None # cumulative
    category: Optional[str] = None
    agents: Optional[set] = None
    invitees: Optional[set] = None
    
class BaseAgent(BaseModel):
    name: str = Field(default="")
    auth: AuthAgent
    description: str = Field(default="")
    human_input_mode: str = Field(default="TERMINATE")
    default_auto_reply: Field(default="")
    system_message: str = Field(default="")
    category: str = Field(default="")
    agents: set = Field(default_factory=set)
    invitees: set = Field(default_factory=set)

class BackendAgent(BaseAgent):
    functions: List[Dict] = Field(default_factory=list)

class OpenAPI2Parameter(BaseModel):
    name: str
    in_: str = Field(..., alias="in")
    description: Optional[str]
    required: Optional[bool] = False
    type_: str = Field(..., alias="type")
    format_: Optional[str] = Field(None, alias="format")
    items: Optional[Dict[str, Any]]

class AddFunctionModel(BaseModel):
    name: str
    auth: AuthAgent
    description: str
    parameters: List[OpenAPI2Parameter]
    category: str
    auth: Optional[AuthAgent] = None
    packages: Optional[List[str]] = None
    code: Optional[str] = None
    class_name: Optional[str] = None

class BackendService:
    @staticmethod
    def delete_backend_agent(data_model: DeleteAgentModel):
        response, err = BackendService.call("delete_agent", data_model.dict(exclude_none=True))
        if err != None:
            return err
        return None
    
    @staticmethod
    def upsert_backend_agent(sender: ConversableAgent, data_model: UpsertAgentModel):
        if sender.auth is None:
            return "No auth, agent has no way to authenticate against backend!"
        data_model.auth = sender.auth
        response, err = BackendService.call("upsert_agent", data_model.dict(exclude_none=True))
        if err != None:
            return err
        return None

    @staticmethod
    def get_backend_agent(data_model: GetAgentModel) -> BackendAgent:
        response, err = BackendService.call("get_agent", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return BackendAgent(response), None

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