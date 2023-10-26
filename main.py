import os
import logging

from fastapi import FastAPI
from autogen.agentchat.user_proxy_agent import UserProxyAgent
from autogen.agentchat.conversable_agent import ConversableAgent
from autogen.agentchat.groupchat import GroupChat, GroupChatManager
app = FastAPI()

# Initialize logging
LOGFILE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'app.log')
logging.basicConfig(filename=LOGFILE_PATH, filemode='w',
                    format='%(asctime)s.%(msecs)03d %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', force=True, level=logging.INFO)

@app.post('/query/')
async def query(user_id: str, api_key: str, query: str):
    user = UserProxyAgent(
        "user",
        llm_config=False,
        default_auto_reply="This is user speaking.",
    )
    admin = ConversableAgent(
        "admin",
        user_id=user_id,
        api_key=api_key,
        human_input_mode="NEVER",
        default_auto_reply="This is admin speaking."
    )
    groupchat = GroupChat(agents=[user, admin], messages=[], max_round=3)
    group_chat_manager = GroupChatManager(
        name="group_manager",
        groupchat=groupchat, 
        user_id=user_id, 
        api_key=api_key,
        default_auto_reply="This is group_manager speaking."
    )
    user.initiate_chat(group_chat_manager, message=query)
