import os
import logging



from autogen import OpenAIWrapper
from fastapi import FastAPI
from pydantic import BaseModel
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from autogen.agentchat.service.function_specs import external_function_specs
from autogen.agentchat.service.agent_models import external_agent_models
from autogen.agentchat.service.group_models import external_group_models
from autogen.agentchat.service import FunctionsService, BackendService, UpsertAgentModel, GetAgentModel, UpsertGroupModel, AuthAgent, GroupService, AgentService, MANAGEMENT, INFO, TERMINATE, CODE_INTERPRETER, FILES, RETRIEVAL
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

def upsert_external_agents(agent_models, auth, client):
    for agent_model in agent_models:
        agent_model.auth = auth
    agents, err = upsert_agents(agent_models, auth, client)
    if err is not None:
        print(f'Could not upsert external agents err: {err}')
    return agents, None

def upsert_external_groups(group_models, auth):
    for group_model in group_models:
        group_model.auth = auth
    groups, err = GroupService.upsert_groups(group_models)
    if err is not None:
        print(f'Error creating groups {err}')
        return
    return groups, None

def upsert_external_functions(sender):
    function_models = []
    for func in external_function_specs:
        func["last_updater"] = sender.name
        function_model, error_message = FunctionsService._create_function_model(sender, func)
        if error_message:
            return error_message
    function_models.append(function_model)
    err = BackendService.upsert_backend_functions(function_models)
    if err is not None:
        return err
    return None

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
def query(input: QueryModel):
    oai_wrapper = OpenAIWrapper(api_key=input.auth.api_key)
    openai_client = oai_wrapper._clients[0]
            
    user_model = UpsertAgentModel(
        name="user_proxy_agent",
        auth=input.auth,
        system_message="I am the proxy between agents and the user. Don't make up questions or topics, it has to come from the user through manual input.",
        description="The proxy to the user to get manual input from user or relay response to the user",
        human_input_mode="ALWAYS",
        default_auto_reply="This is user_proxy_agent speaking.",
        category="planning",
        capability=0
    )
    user_assistant_model = UpsertAgentModel(
        name="user_assistant",
        auth=input.auth,
        description="A generic AI assistant that can analyze problems. I am the assistant to user_proxy_agent.",
        human_input_mode="ALWAYS",
        default_auto_reply="This is the user_assistant speaking.",
        category="planning",
        capability=INFO
    )
    manager_assistant_model = UpsertAgentModel(
        name="manager",
        auth=input.auth,
        description="A generic manager that will analyze if the task is solved, delegate tasks and terminate the program. If the problem is complex and requires a plan you will include part(s) of the plan the groups you task should work on, when you message them. You will coordinate the hiearchy of agents and groups based on this plan.",
        human_input_mode="ALWAYS",
        default_auto_reply="This is the manager speaking.",
        category="planning",
        capability=MANAGEMENT | INFO | TERMINATE
    )
    agent_models = [
        user_model,
        user_assistant_model,
        manager_assistant_model,
    ]
    management_group_model = UpsertGroupModel(
        name="management_group",
        auth=input.auth,
        description="Management group, you will analyze and task user problem to other groups.",
        agents_to_add=["user_proxy_agent", "user_assistant", "manager"],
        locked = True
    )
    group_models = [
        management_group_model,
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
    err = upsert_external_functions(agents[0])
    if err is not None:
        print(f'Could not upsert external functions err: {err}')
    external_agents, err = upsert_external_agents(external_agent_models, input.auth, openai_client)
    if err is not None:
        print(f'Error creating external agents {err}')
        return
    external_groups, err = upsert_external_groups(external_group_models, input.auth)
    if err is not None:
        print(f'Error creating external groups {err}')
        return
    agents[0].initiate_chat(groups[0], message=input.query)