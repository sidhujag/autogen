import os
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from autogen.agentchat.service import BackendAgent, AuthAgent, ConversableAgent, GroupChatManager, MakeService, GroupService, FunctionsService
from autogen.agentchat.service.group_function_specs import(send_message_spec,
    join_group_spec,
    invite_to_group_spec,
    create_group_spec,
    leave_group_spec,
    discover_agents_spec,
    create_or_update_agent,
    discover_functions,
    define_function)
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
    FunctionsService.define_function(agent, send_message_spec)
    FunctionsService.define_function(agent, join_group_spec)
    FunctionsService.define_function(agent, invite_to_group_spec)
    FunctionsService.define_function(agent, create_group_spec)
    FunctionsService.define_function(agent, leave_group_spec)
    FunctionsService.define_function(agent, discover_agents_spec)
    FunctionsService.define_function(agent, create_or_update_agent)
    FunctionsService.define_function(agent, discover_functions)
    FunctionsService.define_function(agent, define_function)

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
    register_base_functions(user)
    user_assistant: ConversableAgent = MakeService.make_agent(BackendAgent(
        name="user_assistant",
        auth=input.auth,
        description="A generic AI assistant that can solve problems",
        human_input_mode="NEVER",
        default_auto_reply="This is the user_assistant speaking.",
        category="user"
    ))
    register_base_functions(user_assistant)
    group_chat_manager: GroupChatManager = MakeService.make_agent(BackendAgent(
        name="group_manager",
        auth=input.auth,
        agents=["user_assistant"], # this will trigger group chat manager to be created
        default_auto_reply="This is group_manager speaking.",
        category="groups"
    ))
    register_base_functions(group_chat_manager)
    GroupService.invite_to_group(sender=group_chat_manager, agent_name="UserProxyAgent", invite_message="Hello UserProxyAgent, please join our group")
    GroupService.join_group(sender=user, group_manager_name="group_manager", hello_message=user._default_auto_reply)
    user.initiate_chat(recipient=group_chat_manager, message=input.query)
