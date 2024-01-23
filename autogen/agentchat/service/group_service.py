
from .. import GroupChatManager, GroupChat
from typing import List
import json
import logging
import asyncio
import copy
import re
from autogen.token_count_utils import token_left
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
DISCOVERY = 1
TERMINATE = 2
OPENAI_CODE_INTERPRETER = 4
OPENAI_RETRIEVAL = 8
OPENAI_FILES = 16
MANAGEMENT = 32

class GroupService:
    current_group_name: str = None
    @staticmethod
    async def start_code_assistance_task(task_func, callback, *args, **kwargs):
        response_callback = None
        try:
            # Run the long-running task
            response = await task_func(*args, **kwargs)
            # Process the results or error using the callback
            if callback:
                response_callback = await callback(*args, response)
        except Exception as e:
            # Handle any unexpected errors here
            logging.error(f"Error in code assistance task: {e}")
        return response_callback

    @staticmethod
    async def process_code_assistance_results(coder, code_repository, command_message, response):
        from . import BackendService, CodeExecInput, CodeRequestInput
        if 'error' in response:
            return json.dumps(response)
        if code_repository.is_forked:
            pr_title = "Feature: Adding new features by agent"
            pr_body = coder.description
            git_response, err = await BackendService.create_github_pull_request(CodeRequestInput(
                repository_name=coder.repository_name,
                title=pr_title,
                body=pr_body,
                branch=coder.repo.active_branch
            ))
            if err is not None:
                logging.error(f"command_pull_request failed: {err}")
                return json.dumps(err)
        else:
            git_response, err = await BackendService.execute_git_command(CodeExecInput(
                workspace=code_repository.workspace,
                command_git_command="push",
            ))
            if err is not None:
                logging.error(f"command_git_command failed: {err}")
        return json.dumps(response)

    @staticmethod
    async def start_nested_task(current_group_name: str, callback, *args, **kwargs):
        from . import GroupService, GetGroupModel
        response_callback = None
        current_group = await GroupService.get_group(GetGroupModel(name=current_group_name))
        if not current_group:
            logging.error("No active group")
            return None
        try:
            # Run the nested chat
            await current_group.a_initiate_chat(*args, **kwargs)
            
            # Process the results using the callback
            if callback:
                response_callback = await callback(current_group, *args, **kwargs)

        except Exception as e:
            # Handle any unexpected errors here
            logging.error(f"Error in nested chat: {e}")
        return response_callback

    @staticmethod
    async def process_nested_chat_results(current_group: GroupChatManager, recipient: GroupChatManager, message: str):    
        from . import BackendService, UpdateComms
        messages = [
            {
                "role": "user",
                "content": f"""Earlier an agent in messaged your group said the following:

    {message}

    Your group, independently in its own context, then worked diligently to address that query. Here is a transcript of that conversation:""",
            }
        ]
        inner_messages = recipient.groupchat.messages
        # The first message just repeats the question, so remove it
        if len(inner_messages) > 1:
            del inner_messages[0]
    
        # copy them to this context
        for inner_message in inner_messages:
            inner_message = copy.deepcopy(inner_message)
            inner_message["role"] = "user"
            messages.append(inner_message)

        messages.append(
            {
                "role": "user",
                "content": f"""
    Read the above conversation and return a final response to the calling agent (group that messaged you) here. The query is repeated here for convenience:

    {message}

    To output the final response:
    
    YOUR FINAL RESPONSE should be a summary but not miss details from the conversation that is pertitent for an answer to questioning agent. You should not assume context is provided to the group that messaged you as contexts are independent. You need to provide the output based on the query on what was requested. YOUR FINAL RESPONSE should include how well the final response captures the requirement of the query based on YOUR FINAL RATING.
    YOUR FINAL RATING should be a number grading for the group like a teacher would grade. On a scale of 10 how well did the group completed the query it was assigned with by another group. Grade YOUR FINAL RESPONSE 0 - fail (no context or answer provided), 5 - improvements needed (calling agent has insufficient context or clarity), 7 - satisfactory (context provided but could be missing some salient points), 10 - exceptional (perfect response to query with all context and details). Just put the number.
    
    Use the following template:
    
    RESPONSE: [YOUR FINAL RESPONSE]
    RATING: [YOUR FINAL RATING]""",
            }
        )
        while token_left(message, "gpt-4-1106-preview") < 4096:
            mid = int(len(messages) / 2)  # Remove from the middle
            del messages[mid]
        response = current_group.client.create(context=None, messages=messages)
        extracted_response = current_group.client.extract_text_or_completion_object(response)[0]
        # Define a regex pattern to find the RATING
        rating_pattern = re.compile(r'RATING:\s*(\d+\.?\d*)\s*')
        if not isinstance(extracted_response, str):
            return str(extracted_response.model_dump(mode="dict"))  # Not sure what to do here
        else:
            # Search for the rating in the response
            rating_match = rating_pattern.search(extracted_response)
            if rating_match:
                # Extract the rating
                rating = rating_match.group(1)
                if float(rating) >= 7:
                    # Increment the communication stats
                    current_group.outgoing[recipient.name] = current_group.outgoing.get(recipient.name, 0) + 1
                    recipient.incoming[current_group.name] = recipient.incoming.get(current_group.name, 0) + 1
                    await BackendService.update_communication_stats(UpdateComms(sender=current_group.name, receiver=recipient.name))
            return extracted_response

    @staticmethod
    async def get_group(group_model) -> GroupChatManager:
        from . import BackendService, MakeService, DeleteGroupModel
        group: GroupChatManager = MakeService.GROUP_REGISTRY.get(group_model.name)
        if group is None:
            backend_groups, err = await BackendService.get_backend_groups([group_model])
            if err is None and backend_groups:
                group, err = await GroupService.make_group(backend_groups[0])
                if err is None and group:
                    MakeService.GROUP_REGISTRY[group_model.name] = group
                else:
                    await BackendService.delete_groups([DeleteGroupModel(name=group_model.name)])
        return group
    
    @staticmethod
    async def get_group_info(name: str, full_description: bool = False) -> str:
        from . import GetGroupModel, GroupInfo, AgentService, MakeService, GetAgentModel
        backend_group = await GroupService.get_group(GetGroupModel(name=name))
        if not backend_group:
            return json.dumps({"error": f"Group({name}) not found"})
        groups_info = []
        agents_dict = {}
        for agent_name in backend_group.agent_names:
            agent = await AgentService.get_agent(GetAgentModel(name=agent_name))
            if agent is None:
                return json.dumps({"error": f"Could not get group agent: {agent_name}"})

            short_description = MakeService._get_short_description(agent.description)
            capability_instr = AgentService.get_capability_instructions(agent.capability)
            agents_dict[agent_name] = {
                "capabilities": capability_instr,
                "description": short_description,
                "files": agent.files
            }
        group_description = backend_group.description if full_description else MakeService._get_short_description(backend_group.description)
        group_info = GroupInfo(
            name=name,
            description=group_description,
            agents=agents_dict,
            incoming=backend_group.incoming,
            outgoing=backend_group.outgoing,
            locked=backend_group.locked,
            current_code_assistant_name=backend_group.current_code_assistant_name
        )
        groups_info.append(group_info.dict(exclude_none=True, exclude={'agent_names', 'auth'}))
        # Return the JSON representation of the groups info
        return json.dumps({"response": groups_info})

    @staticmethod
    async def discover_groups(query: str) -> str:
        from . import BackendService, DiscoverGroupsModel
        response, err = await BackendService.discover_backend_groups(DiscoverGroupsModel(query=query))
        if err is not None:
            return err
        return response

    @staticmethod
    async def upsert_group(group: str, description: str, agents_to_add: List[str] = None, agents_to_remove: List[str] = None, locked: bool = None) -> str:
        from . import UpsertGroupModel, GetGroupModel, GetAgentModel, AgentService
        backend_group = await GroupService.get_group(GetGroupModel(name=group))
        if backend_group:
            if backend_group.locked and (agents_to_add or agents_to_remove or (locked and locked != backend_group.locked) ):
                return json.dumps({"error": f"Group({group}) is locked, agents cannot be added/removed and locked field cannot be modified"})
        else:
            if len(agents_to_add) < 3:
                return json.dumps({"error": f"Could not create group: does not have sufficient agents, at least 3 are needed. Current agents proposed: {', '.join(agents_to_add)}"})
            found_term = False
            for agent_name in agents_to_add:
                agent = await AgentService.get_agent(GetAgentModel(name=agent_name))
                if agent is None:
                    return json.dumps({"error": f"Could not get agent: {agent_name}"})
                if agent.capability & TERMINATE:
                    found_term = True
                    break
            if not found_term:
                return json.dumps({"error": f"Could not create group: does not have someone who can TERMINATE the group. Current agents proposed: {', '.join(agents_to_add)}"})
        group_managers, err = await GroupService.upsert_groups([UpsertGroupModel(
            name=group,
            description=description,
            agents_to_add=agents_to_add,
            agents_to_remove=agents_to_remove,
            locked=locked
        )])
        if err is not None:
            return err
        return json.dumps({"response": f"Group({group}) upserted!"})

    async def start_nested_chat(group: str, message: str) -> str:
        from . import GetGroupModel
        to_group_obj = await GroupService.get_group(GetGroupModel(name=group))
        if to_group_obj is None:
            return json.dumps({"error": f"Could not send message: to_group({group}) not found"})
        current_group = await GroupService.get_group(GetGroupModel(name=GroupService.current_group_name))
        if current_group is None:
            return json.dumps({"error": f"Could not send message: current_group({GroupService.current_group_name}) not found"})
        if current_group.nested_chat_event_task:
            return json.dumps({"error": "A nested chat from this group is still in progress. Please wait until it's completed."})
        if to_group_obj.nested_chat_event_task:
            return json.dumps({"error": "A nested chat in the to_group({to_group}) is still in progress. Please wait until it's completed."})
        if current_group.name == to_group_obj.name:
            return json.dumps({"error": "Cannot initiate a chat to yourself. Are you trying to parallelize? All chats are synchronous."})
        to_group_obj.reset()

        GPTAssistantAgent.cancel_run()
        def setup_nested_chat_event_task():
            async def start_task():
                return await GroupService.start_nested_task(
                    current_group.name,
                    GroupService.process_nested_chat_results,
                    recipient=to_group_obj,
                    message=message
                )
            return start_task

        current_group.nested_chat_event_task = setup_nested_chat_event_task()
        current_group.nested_chat_event_task_msg = f"Message sent from group ({GroupService.current_group_name}) to group ({group})!"
        GroupService.current_group_name = to_group_obj.name
        to_group_obj.parent_group = current_group
        return json.dumps({"response": "Ran nested chat. Please wait for response."})
    
    @staticmethod
    async def _create_group(backend_group):
        from . import GetAgentModel, AgentService, MakeService
        group_agents = []
        for agent_name in backend_group.agent_names:
            agent = await AgentService.get_agent(GetAgentModel(name=agent_name))
            if agent is None:
                return None, json.dumps({"error": f"Could not get group agent: {agent_name}"})
            group_agents.append(agent)

        groupchat = GroupChat(
            agents=group_agents,
            messages=[],
            max_round=50
        )
        return GroupChatManager(
                groupchat=groupchat,
                name=backend_group.name,
                llm_config={"model": "gpt-3.5-turbo-1106", "api_key": MakeService.auth.api_key}
            ), None

    @staticmethod
    async def update_group(group, backend_group):
        from . import MakeService, AgentService, GetAgentModel
        group.description = backend_group.description
        group.incoming = backend_group.incoming
        group.outgoing = backend_group.outgoing
        group.locked = backend_group.locked
        group.current_code_assistant_name = backend_group.current_code_assistant_name
        agent_names = group.agent_names
        for agent_name in backend_group.agent_names:
            if agent_name not in agent_names:
                agent = await AgentService.get_agent(GetAgentModel(name=agent_name))
                if agent is None:
                    return None, json.dumps({"error": f"Could not get group agent: {agent_name}"})
                group.groupchat.agents.append(agent)
        MakeService.GROUP_REGISTRY[group.name] = group
        return group, None
    
    @staticmethod
    async def make_group(backend_group):
        from . import MakeService
        group, err = await GroupService._create_group(backend_group)
        if err is not None:
            return None, err
        group.description = backend_group.description
        group.incoming = backend_group.incoming
        group.outgoing = backend_group.outgoing
        group.locked = backend_group.locked
        group.current_code_assistant_name = backend_group.current_code_assistant_name
        MakeService.GROUP_REGISTRY[group.name] = group
        return group, None

    @staticmethod
    async def upsert_groups(upsert_models):
        from . import BackendService, GetGroupModel, MakeService, DeleteGroupModel
        # Step 1: Upsert all groups in batch
        err = await BackendService.upsert_backend_groups(upsert_models)
        if err and err != json.dumps({"error": "No groups were upserted, no changes found!"}):
            print(f'err {err}')
            return None, err
        # Step 2: Retrieve all groups from backend in batch
        get_group_models = [GetGroupModel(name=model.name) for model in upsert_models]
        backend_groups, err = await BackendService.get_backend_groups(get_group_models)
        if err:
            return None, err
        if len(backend_groups) == 0:
            return None, json.dumps({"error": "Could not fetch groups from backend"})

        # Step 3: Update local group registry
        successful_groups = []
        for backend_group in backend_groups:
            mgr = MakeService.GROUP_REGISTRY.get(backend_group.name)
            if mgr is None:
                mgr, err = await GroupService.make_group(backend_group)
                if err is not None:
                    await BackendService.delete_groups([DeleteGroupModel(name=backend_group.name)])
                    return None, err
            else:
                mgr, err = await GroupService.update_group(mgr, backend_group)
                if err is not None:
                    return None, err
            successful_groups.append(mgr)
        return successful_groups, None
