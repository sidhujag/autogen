import os
import logging



from autogen import OpenAIWrapper
from fastapi import FastAPI
from pydantic import BaseModel
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from autogen.agentchat.service.function_specs import external_function_specs
from autogen.agentchat.service.agent_models import external_agent_models
from autogen.agentchat.service.group_models import external_group_models
from autogen.oai.openai_utils import retrieve_assistants_by_name
from autogen.agentchat.service import MakeService, FunctionsService, BackendService, UpsertAgentModel, UpsertGroupModel, AuthAgent, GroupService, AgentService, MANAGEMENT, INFO, TERMINATE
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

def upsert_external_agents(agent_models):
    agents, err = upsert_agents(agent_models)
    if err is not None:
        print(f'Could not upsert external agents err: {err}')
        return None, None
    return agents, None

def upsert_external_groups(group_models):
    groups, err = GroupService.upsert_groups(group_models)
    if err is not None:
        print(f'Error creating groups {err}')
        return None, None
    return groups, None

def upsert_external_functions(sender):
    function_models = []
    for func in external_function_specs:
        func["last_updater"] = sender.name
        func["status"] = "accepted"
        function_model, error_message = FunctionsService._create_function_model(sender, func)
        if error_message:
            return error_message
        function_models.append(function_model)
    err = BackendService.upsert_backend_functions(function_models)
    if err is not None:
        return err
    return None

def upsert_agents(models):
    for model in models:
        id = None
        print(f'upsert_agent: {model.name}')
        candidate_assistants = retrieve_assistants_by_name(MakeService.openai_client, model.name)
        if candidate_assistants:
            if len(candidate_assistants) > 1:
                for candidate_assistant in candidate_assistants:
                    MakeService.openai_client.beta.assistants.delete(assistant_id=candidate_assistant.id)
                openai_assistant = MakeService.openai_client.beta.assistants.create(
                    name=model.name,
                    instructions="",
                    tools=[],
                    model="gpt-4-1106-preview",
                )
                id = openai_assistant.id
            else:
                id = candidate_assistants[0].id
        else:
            openai_assistant = MakeService.openai_client.beta.assistants.create(
                name=model.name,
                instructions="",
                tools=[],
                model="gpt-4-1106-preview",
            )
            id = openai_assistant.id
        model.assistant_id = id
    agents, err = AgentService.upsert_agents(models)
    if err is not None:
        return None, err
    return agents, None

@app.post('/delete_all_assistants/')
def delete_all_assistants(input: QueryModel):
    oai_wrapper = OpenAIWrapper(api_key=input.auth.api_key)
    openai_client = oai_wrapper._clients[0]
    MakeService.auth = input.auth
    MakeService.openai_client = openai_client
    assistants = MakeService.openai_client.beta.assistants.list(limit=100)
    for assistant in assistants:
        MakeService.openai_client.beta.assistants.delete(assistant_id=assistant.id)
    return "success"

@app.post('/query/')
async def query(input: QueryModel):
    oai_wrapper = OpenAIWrapper(api_key=input.auth.api_key)
    openai_client = oai_wrapper._clients[0]
    MakeService.auth = input.auth
    MakeService.openai_client = openai_client           
    user_model = UpsertAgentModel(
        name="user_proxy",
        system_message="Proxy between the management group and the user. Your interactions will allow the user to input a message to guide the management group with user feedback. Works with manager and manager_assistant.",
        description="Use to be able to get feedback from the user.",
        human_input_mode="ALWAYS",
        default_auto_reply="This is user_proxy speaking.",
        category="planning",
        capability=0
    )
    manager_assistant_model = UpsertAgentModel(
        name="manager_assistant",
        system_message="Assist the manager in formulating a well-rounded and informed answer before termination. Provides general feedback to manager prior to actions. Works with user_proxy and manager_assistant. You can use user_proxy to get user feedback. You provide feedback to the manager before manager takes an action.",
        description="Helps the manager analyze a plan, an answer or the final response for the problem before it is terminated.",
        human_input_mode="NEVER",
        default_auto_reply="This is the manager_assistant speaking.",
        category="planning",
        capability=0
    )
    manager_model = UpsertAgentModel(
        name="manager",
        system_message="Delegate tasks and plans across hiearchy of agents and solves the problem before terminating the group. If the problem is complex and requires a plan you will include part(s) of the plan the groups you task should work on, when you message them. You will coordinate the hiearchy of agents and groups based on this plan. You work in a chain-of-thought or tree-of-thought pattern. You can use user_proxy to get user feedback. You will get feedback from manager_assistant as needed.",
        description="A general manager that will analyze if the task is solved, delegate tasks and terminate the program.",
        human_input_mode="ALWAYS",
        default_auto_reply="This is the manager speaking.",
        category="planning",
        capability=MANAGEMENT | INFO | TERMINATE
    )
    agent_models = [
        user_model,
        manager_model,
        manager_assistant_model,
    ]
    management_group_model = UpsertGroupModel(
        name="management_group",
        description="Management group, you will analyze and task user problem to other groups. For complex problems use the planning group, where chain-of-thought or tree-of-thought pattern should be used with the plan to delegate subsets of the plan to other groups, sometimes getting the plan updated as needed due to feedback. The group consists of user_proxy, manager, and manager_assistant.",
        agents_to_add=["user_proxy", "manager_assistant", "manager"],
        locked = True
    )
    group_models = [
        management_group_model,
    ]
    agents: List[GPTAssistantAgent] = None
    agents, err = upsert_agents(agent_models)
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
    external_agents, err = upsert_external_agents(external_agent_models)
    if err is not None:
        print(f'Error creating external agents {err}')
        return
    external_groups, err = upsert_external_groups(external_group_models)
    if err is not None:
        print(f'Error creating external groups {err}')
        return
    await agents[0].a_initiate_chat(groups[0], message=input.query)