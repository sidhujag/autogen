import os
import logging

from autogen import OpenAIWrapper
from fastapi import FastAPI
from pydantic import BaseModel
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from autogen.agentchat.service import UpsertAgentModel, GetAgentModel, UpsertGroupModel, AuthAgent, GroupService, AgentService, MANAGEMENT, GROUP_INFO, CODE_INTERPRETER_TOOL, FILES, RETRIEVAL_TOOL
from typing import List
from hanging_threads import start_monitoring
monitoring_thread = start_monitoring()
app = FastAPI()

# Initialize logging
LOGFILE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'app.log')
logging.basicConfig(filename=LOGFILE_PATH, filemode='w',
                    format='%(asctime)s.%(msecs)03d %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', force=True, level=logging.INFO)

class QueryModel(BaseModel):
    auth: AuthAgent
    query: str

def upsert_agents(models, auth, client):
    for model in models:
        agent = AgentService.get_agent(GetAgentModel(auth=auth, name=model.name))
        id = None
        if agent is None:
            # place holder to get assistant id
            openai_assistant = client.beta.assistants.create(
                name=model.name,
                instructions="",
                tools=[],
                model="gpt-4-1106-preview",
            )
            id = openai_assistant.id
        else:
            id = agent._openai_assistant.id
        model.assistant_id = id
    agents, err = AgentService.upsert_agents(models)
    if err is not None:
        return None, err
    return agents, None

@app.post('/query/')
async def query(input: QueryModel):
    oai_wrapper = OpenAIWrapper(api_key=input.auth.api_key)
    openai_client = oai_wrapper._clients[0]
            
    user_model = UpsertAgentModel(
        name="UserProxyAgent",
        auth=input.auth,
        system_message="I am the proxy between agents and the user. Don't make up questions or topics, it has to come from the user through manual input.",
        description="The proxy to the user to get manual input from user or relay response to the user",
        human_input_mode="ALWAYS",
        default_auto_reply="This is UserProxyAgent speaking.",
        category="user",
    )
    user_assistant_model = UpsertAgentModel(
        name="user_assistant",
        auth=input.auth,
        description="A generic AI assistant that can solve problems",
        human_input_mode="ALWAYS",
        default_auto_reply="This is the user_assistant speaking.",
        category="user",
        capability=MANAGEMENT | GROUP_INFO | CODE_INTERPRETER_TOOL | FILES | RETRIEVAL_TOOL
    )
    manager_assistant_model = UpsertAgentModel(
        name="manager",
        auth=input.auth,
        description="A generic manager that can analyze and tell other agents what to do",
        human_input_mode="ALWAYS",
        default_auto_reply="This is the manager speaking.",
        category="planning",
        capability=MANAGEMENT | GROUP_INFO
    )
    coder_assistant_model = UpsertAgentModel(
        name="coder_assistant",
        auth=input.auth,
        description="A generic AI assistant that can create elegant code to problems.",
        human_input_mode="ALWAYS",
        default_auto_reply="This is the coder_assistant speaking.",
        category="programming",
    )
    agent_models = [
        user_model,
        user_assistant_model,
        manager_assistant_model,
        coder_assistant_model
    ]
    management_group_model = UpsertGroupModel(
        name="ManagementGroup",
        auth=input.auth,
        description="Management group, you will delegate user problem to other groups.",
        agents_to_add=["UserProxyAgent", "user_assistant", "manager"]
    )
    planning_group_model = UpsertGroupModel(
        name="PlanningGroup",
        auth=input.auth,
        description="Planning group, you will get a problem where you need to create a plan, and assemble a hiearchical organization of groups.",
        agents_to_add=["UserProxyAgent", "user_assistant", "coder_assistant"]
    )
    group_models = [
        management_group_model,
        planning_group_model
    ]
    agents: List[GPTAssistantAgent] = None
    agents, err = upsert_agents(agent_models, input.auth, openai_client)
    if err is not None:
        print(f'Error creating agents {err}')
        return
    groups, err = GroupService.upsert_groups(group_models)
    if err is not None:
        print(f'Error creating groups {err}')
        return
    agents[0].initiate_chat(groups[0], message=input.query)
    
    