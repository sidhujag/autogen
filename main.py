import os
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from autogen.agentchat import ConversableAgent, GroupChatManager
from autogen.agentchat.service import UpsertAgentModel, AuthAgent, MakeService, GroupService, FunctionsService
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

def register_base_functions(agents: List[ConversableAgent]):
    for agent in agents:
        response = FunctionsService.define_functions(agent, group_function_specs)
        if response != "Function(s) added successfully":
            print(f'define_functions err {response}')
            return

@app.post('/query/')
async def query(input: QueryModel):
    user_model = UpsertAgentModel(
        name="UserProxyAgent",
        auth=input.auth,
        system_message="Pass me messages so I can relay back to the user.",
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
    group_chat_manager_model = UpsertAgentModel(
        name="group_manager",
        auth=input.auth,
        human_input_mode="ALWAYS",
        default_auto_reply="This is group_manager speaking.",
        category="groups"
    )
    models = [
        user_model,
        user_assistant_model,
        group_chat_manager_model
    ]
    agents, err = MakeService.upsert_agents(models)
    if err is not None:
        print(f'Error creating agents {err}')
        return
    register_base_functions(agents)
    group_agent_name="group_agent"
    GroupService.create_group(agents[2], group_agent_name=group_agent_name, group_description="Management group", invitees=[user_assistant_model.name])
    GroupService.invite_to_group(sender=agents[2], agent_name=user_model.name, group_agent_name=group_agent_name, invite_message=f"Hello {user_model.name}, please join our group")
    GroupService.join_group(sender=agents[0], group_agent_name=group_agent_name, hello_message=agents[0]._default_auto_reply)
    GroupService.join_group(sender=agents[1], group_agent_name=group_agent_name, hello_message=agents[1]._default_auto_reply)
    agents[0].initiate_chat(recipient=agents[1], message=input.query)
    
    
