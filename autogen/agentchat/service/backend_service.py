
import requests
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from .. import ConversableAgent

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
    description: Optional[str] = None
    system_message: Optional[str] = None
    function_names: Optional[List[str]] = None # cumulative
    category: Optional[str] = None
    agents: Optional[List[Dict]] = None
    invitees: Optional[List[str]] = None
    
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

    def delete_agent(self, sender: ConversableAgent, data_model: DeleteAgentModel):
        auth: AuthAgent = self.AUTH.get(sender.name)
        if auth is None:
            return None, "No auth, agent has no way to authenticate against backend!"
        data_model.auth = auth
        response, err = self.call("delete_agent", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    def upsert_agent_data(self, sender: ConversableAgent, data_model: UpsertAgentModel):
        auth: AuthAgent = self.AUTH.get(sender.name)
        if auth is None:
            return None, "No auth, agent has no way to authenticate against backend!"
        data_model.auth = auth
        response, err = self.call("upsert_agent", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None
        
    def get_agent_data(self, sender: ConversableAgent, data_model: GetAgentModel):
        auth: AuthAgent = self.AUTH.get(sender.name)
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
        return response, None

    def add_function(self, sender: ConversableAgent, data_model: AddFunctionModel):
        auth: AuthAgent = self.AUTH.get(sender.name)
        if auth is None:
            return None, "No auth, agent has no way to authenticate against backend!"
        data_model.auth = auth
        response, err = self.call("add_functions", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    def discover_functions(self, sender: ConversableAgent, data_model: DiscoverFunctionsModel):
        auth: AuthAgent = self.AUTH.get(sender.name)
        if auth is None:
            return None, "No auth, agent has no way to authenticate against backend!"
        data_model.auth = auth
        response, err = self.call("discover_functions", data_model.dict(exclude_none=True))
        if err != None:
            return None, err
        return response, None

    def discover_agents(self, sender: ConversableAgent, data_model: DiscoverAgentsModel):
        auth: AuthAgent = self.AUTH.get(sender.name)
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