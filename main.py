import os
import logging

from fastapi import FastAPI
from autogen.agentchat.user_proxy_agent import UserProxyAgent
from autogen.agentchat.conversable_agent import ConversableAgent
from autogen.agentchat.groupchat import GroupChat, GroupChatManager
from pydantic import BaseModel

app = FastAPI()

# Initialize logging
LOGFILE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'app.log')
logging.basicConfig(filename=LOGFILE_PATH, filemode='w',
                    format='%(asctime)s.%(msecs)03d %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', force=True, level=logging.INFO)

class QueryModel(BaseModel):
    user_id: str
    api_key: str
    query: str

@app.post('/query/')
async def query(input: QueryModel):
    user = UserProxyAgent(
        "UserProxyAgent",
        description="The proxy to the user to get input or relay response",
        llm_config=False,
        default_auto_reply="This is UserProxyAgent speaking.",
    )
    assistant = ConversableAgent(
        "user_assistant",
        user_id=input.user_id,
        api_key=input.api_key,
        human_input_mode="NEVER",
        default_auto_reply="This is the user_assistant speaking."
    )
    groupchat = GroupChat(agents=[{"name": user.name, "description": user.description}], invitees=[])
    group_chat_manager = GroupChatManager(
        name="group_manager",
        groupchat=groupchat, 
        user_id=input.user_id, 
        api_key=input.api_key,
        default_auto_reply="This is group_manager speaking."
    )
    user.invite_to_group("user_assistant", "group_manager", "Hello user_assistant, please join our group.")
    assistant.join_group("group_manager", "Hello this is the user assistant joining!")
    user.initiate_chat(group_chat_manager, message=input.query)
