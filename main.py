import os
import logging

from fastapi import FastAPI
from autogen.agentchat.conversable_agent import ConversableAgent
from pydantic import BaseModel
from autogen.agentchat import MakeService, GroupService
from autogen.agentchat.service.backend_service import BackendAgent, AuthAgent
app = FastAPI()

# Initialize logging
LOGFILE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'app.log')
logging.basicConfig(filename=LOGFILE_PATH, filemode='w',
                    format='%(asctime)s.%(msecs)03d %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', force=True, level=logging.INFO)

class QueryModel(BaseModel):
    auth: AuthAgent
    query: str

@app.post('/query/')
async def query(input: QueryModel):
    user: ConversableAgent = MakeService.make_agent(BackendAgent(
        name="UserProxyAgent",
        auth=input.auth,
        system_message="Pass me messages so I can relay back to the user.",
        description="The proxy to the user to get input or relay response",
        human_input_mode="ALWAYS",
        default_auto_reply="This is UserProxyAgent speaking.",
        category="user"
    ))
    user_assistant: ConversableAgent = MakeService.make_agent(BackendAgent(
        name="user_assistant",
        auth=input.auth,
        system_message="Pass me messages so I can relay back to the user.",
        description="The proxy to the user to get input or relay response",
        human_input_mode="NEVER",
        default_auto_reply="This is the user_assistant speaking.",
        category="user"
    ))
    group_chat_manager: ConversableAgent = MakeService.make_agent(BackendAgent(
        name="group_manager",
        auth=input.auth,
        agents=["user_assistant"],
        default_auto_reply="This is group_manager speaking.",
        category="groups"
    ))
    GroupService.invite_to_group(group_chat_manager, user, "Hello UserProxyAgent, please join our group")
    GroupService.join_group(user, "group_manager", user.default_auto_reply)
    user.initiate_chat(group_chat_manager, message=input.query)
