import os
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from autogen.agentchat import ConversableAgent
from autogen.agentchat.service import UpsertAgentModel, AuthAgent, MakeService, GroupService, FunctionsService, AgentService
from autogen.agentchat.service.group_function_specs import group_function_specs
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
    list_fn_names = [fn_spec["name"] for fn_spec in group_function_specs]
    for agent_model in agent_models:
        response = FunctionsService.define_functions(agent_model, group_function_specs)
        if response != "Functions defined! An agent can add them now":
            print(f'define_functions err {response}')
            return
        agent_model.functions_to_add = list_fn_names
    print("All functions registered.")

@app.post('/query/')
async def query(input: QueryModel):
    user_model = UpsertAgentModel(
        name="UserProxyAgent",
        auth=input.auth,
        system_message="I am the proxy between agents and the user. The user initiates the original query through me and later any questions for the user can be sent to me so I can ask the user for manual input.",
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
    agents: List[ConversableAgent] = None
    agents, err = MakeService.upsert_agents(models)
    if err is not None:
        print(f'Error creating agents {err}')
        return
    response, group_manager = GroupService.create_or_update_group(sender=agents[0], group="group_name", description="Management group", agents_to_add=["UserProxyAgent", "user_assistant"])
    agents[0].initiate_chat(group_manager, message=input.query)
    
    
