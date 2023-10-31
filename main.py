import os
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from autogen.agentchat import ConversableAgent, GroupChatManager
from autogen.agentchat.service import UpsertAgentModel, AuthAgent, MakeService, GroupService, FunctionsService
from autogen.agentchat.service.group_function_specs import group_function_specs
app = FastAPI()

# Initialize logging
LOGFILE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'app.log')
logging.basicConfig(filename=LOGFILE_PATH, filemode='w',
                    format='%(asctime)s.%(msecs)03d %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', force=True, level=logging.INFO)

class QueryModel(BaseModel):
    auth: AuthAgent
    query: str

def register_base_functions(agent: ConversableAgent):
    response = FunctionsService.define_functions(agent, group_function_specs)
    if response != "Function(s) added successfully":
        print(f'define_functions err {response}')
        return

@app.post('/query/')
async def query(input: QueryModel):
    user: ConversableAgent
    user, err = MakeService.upsert_agent(UpsertAgentModel(
        name="UserProxyAgent",
        auth=input.auth,
        system_message="Pass me messages so I can relay back to the user.",
        description="The proxy to the user to get input or relay response",
        human_input_mode="ALWAYS",
        default_auto_reply="This is UserProxyAgent speaking.",
        category="user"
    ))
    if err is not None:
        print(f'Error creating UserProxyAgent {err}')
        return
    register_base_functions(user)
    user_assistant: ConversableAgent
    user_assistant, err = MakeService.upsert_agent(UpsertAgentModel(
        name="user_assistant",
        auth=input.auth,
        description="A generic AI assistant that can solve problems",
        human_input_mode="ALWAYS",
        default_auto_reply="This is the user_assistant speaking.",
        category="user"
    ))
    if err is not None:
        print(f'Error creating user_assistant {err}')
        return
    register_base_functions(user_assistant)
    group_chat_manager: GroupChatManager
    group_chat_manager, err = MakeService.upsert_agent(UpsertAgentModel(
        name="group_manager",
        auth=input.auth,
        human_input_mode="ALWAYS",
        agents={"user_assistant": True}, # this will trigger group chat manager to be created
        default_auto_reply="This is group_manager speaking.",
        category="groups"
    ))
    if err is not None:
        print(f'Error creating group_manager {err}')
        return
    register_base_functions(group_chat_manager)
    GroupService.invite_to_group(sender=group_chat_manager, agent_name="UserProxyAgent", group_manager_name="group_manager", invite_message="Hello UserProxyAgent, please join our group")
    GroupService.join_group(sender=user, group_manager_name="group_manager", hello_message=user._default_auto_reply)
    user.initiate_chat(recipient=group_chat_manager, message=input.query)
