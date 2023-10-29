
import requests
from pydantic import BaseModel
from typing import Dict, List, Optional, Union

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
    description: Optional[str] = None
    system_message: Optional[str] = None
    function_names: Optional[List[str]] = None # cumulative
    category: Optional[str] = None
    agents: Optional[List[Dict]] = None
    invitees: Optional[List[str]] = None
    
class BaseAgent(BaseModel):
    name: str = Field(default="")
    namespace_id: str = Field(default="")
    description: str = Field(default="")
    human_input_mode: str = Field(default="TERMINATE")
    system_message: str = Field(default="")
    category: str = Field(default="")
    agents: List[Dict] = Field(default_factory=list)
    invitees: List[str] = Field(default_factory=list)

class BackendAgent(BaseAgent):
    functions: List[Dict] = Field(default_factory=list)

class AddFunctionModel(BaseModel):
    name: str
    auth: AuthAgent
    description: str
    arguments: Dict[str, Union[str, Dict]] = None
    required: List[str] = None
    category: str
    packages: Optional[List[str]] = None
    code: Optional[str] = None
    class_name: Optional[str] = None

class BackendService:
    AUTH: Dict[str, AuthAgent] = {}
    
    def get_auth(self, agent_name) -> AuthAgent:
        return self.AUTH.get(agent_name)

    def set_auth(self, agent_name, agent_data) -> AuthAgent:
        self.AUTH[agent_name] = agent_data['auth']
        return self.AUTH[agent_name]

    def delete_backend_agent(self, sender: str, data_model: DeleteAgentModel):
        auth: AuthAgent = self.AUTH.get(sender)
        if auth is None:
            return None, "No auth, agent has no way to authenticate against backend!"
        data_model.auth = auth
        response, err = self.call("delete_agent", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    def upsert_backend_agent(self, sender: str, data_model: UpsertAgentModel):
        auth: AuthAgent = self.AUTH.get(sender)
        if auth is None:
            return None, "No auth, agent has no way to authenticate against backend!"
        data_model.auth = auth
        response, err = self.call("upsert_agent", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None
        
    def get_backend_agent(self, sender: str, data_model: GetAgentModel) -> BackendAgent:
        auth: AuthAgent = self.AUTH.get(sender)
        if auth is None:
            return None, "No auth, agent has no way to authenticate against backend!"
        data_model.auth = auth
        response, err = self.call("get_agent", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        if 'name' not in response or len(response["name"]) == 0:
            return None, "invalid response"
        keys = ['description', 'system_message', 'functions']
        if not all(key in response for key in keys):
            missing_keys = [key for key in keys if key not in response]
            return None, f"Error: Missing keys in agent_data: {', '.join(missing_keys)}"
        response["auth"] = auth
        return BackendAgent(response), None

    def add_backend_function(self, sender: str, data_model: AddFunctionModel):
        auth: AuthAgent = self.AUTH.get(sender)
        if auth is None:
            return None, "No auth, agent has no way to authenticate against backend!"
        data_model.auth = auth
        response, err = self.call("add_function", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    def discover_backend_functions(self, sender: str, data_model: DiscoverFunctionsModel):
        auth: AuthAgent = self.AUTH.get(sender)
        if auth is None:
            return None, "No auth, agent has no way to authenticate against backend!"
        data_model.auth = auth
        response, err = self.call("discover_functions", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    def discover_backend_agents(self, sender: str, data_model: DiscoverAgentsModel):
        auth: AuthAgent = self.AUTH.get(sender)
        if auth is None:
            return None, "No auth, agent has no way to authenticate against backend!"
        data_model.auth = auth
        response, err = self.call("discover_agents", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    def call(self, endpoint, json):   
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