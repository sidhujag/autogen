import os
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from autogen.agentchat import DiscoverableConversableAgent
from autogen.agentchat.service import UpsertAgentModel, AuthAgent, MakeService, FunctionsService
from autogen.agentchat.service.agent_function_specs import agent_function_specs
from typing import List
app = FastAPI()

# Initialize logging
LOGFILE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'app.log')
logging.basicConfig(filename=LOGFILE_PATH, filemode='w',
                    format='%(asctime)s.%(msecs)03d %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', force=True, level=logging.INFO)

class QueryModel(BaseModel):
    auth: AuthAgent
    query: str


def register_base_functions(agent_models: List[UpsertAgentModel]):
    list_fn_names = [fn_spec["name"] for fn_spec in agent_function_specs]
    for agent_model in agent_models:
        response = FunctionsService.define_functions(agent_model, agent_function_specs)
        if response != "Functions created or updated! If you want to use the functions now, you may want to add to an agent":
            print(f'define_functions err {response}')
            return
        agent_model.functions_to_add = list_fn_names
    print("All functions registered.")

@app.post('/query/')
async def query(input: QueryModel):
    user_model = UpsertAgentModel(
        name="UserProxyAgent",
        auth=input.auth,
        system_message="I am the proxy between agents and the user.",
        description="The proxy to the user to get input or relay response",
        human_input_mode="ALWAYS",
        default_auto_reply="This is UserProxyAgent speaking.",
        category="user"
    )
    user_assistant_model = UpsertAgentModel(
        name="user_assistant",
        auth=input.auth,
        description="A generic AI assistant that can solve problems",
        human_input_mode="ALWAYS",
        default_auto_reply="This is the user_assistant speaking.",
        category="user"
    )
    models = [
        user_model,
        user_assistant_model
    ]
    register_base_functions(models)
    agents: List[DiscoverableConversableAgent] = None
    agents, err = MakeService.upsert_agents(models)
    if err is not None:
        print(f'Error creating agents {err}')
        return
    agents[0].initiate_chat(agents[1], message=input.query)
    
    
