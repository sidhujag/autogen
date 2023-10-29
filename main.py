import os
import logging

from fastapi import FastAPI
from autogen.agentchat.conversable_agent import ConversableAgent
from pydantic import BaseModel
from autogen.agentchat import MakeService, GroupService
from autogen.agentchat.service.backend_service import BackendAgent, AuthAgent
from autogen.agentchat.groupchat import GroupChatManager
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
        description="A generic AI assistant that can solve problems",
        human_input_mode="NEVER",
        default_auto_reply="This is the user_assistant speaking.",
        category="user"
    ))
    group_chat_manager: GroupChatManager = MakeService.make_agent(BackendAgent(
        name="group_manager",
        auth=input.auth,
        agents=["user_assistant"], # this will trigger group chat manager to be created
        default_auto_reply="This is group_manager speaking.",
        category="groups"
    ))
    GroupService.invite_to_group(sender=group_chat_manager, agent_name="UserProxyAgent", invite_message="Hello UserProxyAgent, please join our group")
    GroupService.join_group(sender=user, group_manager_name="group_manager", hello_message=user._default_auto_reply)
    user.initiate_chat(recipient=group_chat_manager, message=input.query)