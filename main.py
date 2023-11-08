import os
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from autogen.agentchat import ConversableAgent
from autogen.agentchat.service import UpsertAgentModel, UpsertGroupModel, AuthAgent, GroupService, AgentService, FunctionsService
from autogen.agentchat.service.function_specs import function_specs
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
    list_fn_names = [fn_spec["name"] for fn_spec in function_specs]
    for agent_model in agent_models:
        response = FunctionsService.define_functions(agent_model, function_specs)
        if response != "Functions created or updated! You can add them to agent(s) now.":
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
    agent_models = [
        user_model,
        user_assistant_model
    ]
    management_group_model = UpsertGroupModel(
        name="ManagementGroup",
        auth=input.auth,
        description="Management group, you will delegate user problem to other groups.",
        agents_to_add=["UserProxyAgent", "user_assistant"]
    )
    planning_group_model = UpsertAgentModel(
        name="PlanningGroup",
        auth=input.auth,
        description="Planning group, you will get a problem where you need to create a plan, and assemble a hiearchical organization of groups. You get input from another group and return response after your done. You can also delegate work to other groups, but still filter respond to group that delegated to you.",
        human_input_mode="ALWAYS",
        agents_to_add=[]
    )
    agent_models = [
        user_model,
        user_assistant_model
    ]
    group_models = [
        management_group_model,
        planning_group_model
    ]
    register_base_functions(agent_models)
    agents: List[ConversableAgent] = None
    agents, err = AgentService.upsert_agents(agent_models)
    if err is not None:
        print(f'Error creating agents {err}')
        return
    groups, err = GroupService.upsert_groups(group_models)
    if err is not None:
        print(f'Error creating groups {err}')
        return
    agents[0].initiate_chat(groups[0], message=input.query)
    
    
