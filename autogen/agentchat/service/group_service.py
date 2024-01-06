
from .. import GroupChatManager, GroupChat
from typing import List
import json
import logging
import asyncio
import copy
import re
from autogen.token_count_utils import token_left
INFO = 1
TERMINATE = 2
OPENAI_CODE_INTERPRETER = 4
OPENAI_RETRIEVAL = 8
OPENAI_FILES = 16
MANAGEMENT = 32

class GroupService:
    current_group: GroupChatManager = None
    @staticmethod
    async def start_long_running_task(current_group: GroupChatManager, task_func, callback, *args, **kwargs):
        if not current_group:
            logging.error("No active group")
            return
        current_group.task_completed_msg = ""
        current_group.task_completed_event.set()
        try:
            # Run the long-running task
            response, err = task_func(*args, **kwargs)
            
            # Process the results or error using the callback
            if callback:
                await callback(current_group, response, err)

        except Exception as e:
            # Handle any unexpected errors here
            logging.error(f"Error in long-running task: {e}")
        finally:
            # Clear the event to indicate completion
            current_group.task_completed_event.clear()

    @staticmethod
    async def process_task_results(current_group: GroupChatManager, response, err):
        if err:
            current_group.task_completed_msg = err
        else:
            current_group.task_completed_msg = json.dumps({"response": f"Task completed with response: {response}"})
    
    @staticmethod
    async def start_nested_task(current_group: GroupChatManager, task_func, callback, *args, **kwargs):
        print(f'start_nested_task from current_group {current_group.name}')
        if not current_group:
            logging.error("No active group")
            return
        current_group.nested_chat_completed_msg = ""
        current_group.nested_chat_completed_event.set()
        try:
            # Run the nested chat
            await task_func(*args, **kwargs)
            
            # Process the results using the callback
            if callback:
                await callback(current_group, *args, **kwargs)

        except Exception as e:
            # Handle any unexpected errors here
            logging.error(f"Error in long-running task: {e}")
        finally:
            # clear the event to indicate completion
            current_group.nested_chat_completed_event.clear()

    @staticmethod
    async def process_nested_chat_results(current_group: GroupChatManager, recipient: GroupChatManager, message: str):    
        print(f'process_nested_chat_results from current_group {current_group.name} recipient {recipient.name} message {message}')
        from . import BackendService, UpdateComms
        messages = [
            {
                "role": "user",
                "content": f"""Earlier an agent in another group said the following:

    {message}

    Your group then worked diligently to address that query. Here is a transcript of that conversation:""",
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
    Read the above conversation and return a final response to the calling agent here. The query is repeated here for convenience:

    {message}

    To output the final response:
    
    YOUR FINAL RESPONSE should be a summary but not miss details from the conversation that is pertitent for an answer to questioning agent. YOUR FINAL RESPONSE should include how well it answered the query based on YOUR FINAL RATING.
    YOUR FINAL RATING should be a number grading for the group like a teacher would grade. On a scale of 10 how well did the group completed the query it was assigned with by another group. 0 - fail, 5 - improvements needed, 7 - satisfactory, 10 - exceptional. Just put the number.
    
    Use the following template:
    
    RESPONSE: [YOUR FINAL RESPONSE]
    RATING: [YOUR FINAL RATING]""",
            }
        )

        while token_left(messages) < 4096:
            mid = int(len(messages) / 2)  # Remove from the middle
            del messages[mid]
    
        response = current_group.client.create(context=None, messages=messages)
        extracted_response = current_group.client.extract_text_or_completion_object(response)[0]
        # Define a regex pattern to find the RATING
        rating_pattern = re.compile(r'RATING:\s*(\d+\.?\d*)\s*')
        if not isinstance(extracted_response, str):
            current_group.nested_chat_completed_msg = str(extracted_response.model_dump(mode="dict"))  # Not sure what to do here
        else:
            # Search for the rating in the response
            rating_match = rating_pattern.search(extracted_response)
            if rating_match:
                # Extract the rating
                rating = rating_match.group(1)
                if rating >= 7:
                    # Increment the communication stats
                    current_group.outgoing[recipient.name] = current_group.outgoing.get(recipient.name, 0) + 1
                    recipient.incoming[current_group.name] = recipient.incoming.get(current_group.name, 0) + 1
                    BackendService.update_communication_stats(UpdateComms(sender=current_group.name, receiver=recipient.name))
            current_group.nested_chat_completed_msg = extracted_response


    @staticmethod
    def get_group(group_model) -> GroupChatManager:
        from . import BackendService, MakeService, DeleteGroupModel
        group: GroupChatManager = MakeService.GROUP_REGISTRY.get(group_model.name)
        if group is None:
            backend_groups, err = BackendService.get_backend_groups([group_model])
            if err is None and backend_groups:
                group, err = GroupService.make_group(backend_groups[0])
                if err is None and group:
                    MakeService.GROUP_REGISTRY[group_model.name] = group
                else:
                    BackendService.delete_groups([DeleteGroupModel(name=group_model.name)])
        return group
    
    @staticmethod
    def get_group_info(name: str, full_description: bool = False) -> str:
        from . import GetGroupModel, GroupInfo, AgentService, MakeService, GetAgentModel
        backend_group = GroupService.get_group(GetGroupModel(name=name))
        if not backend_group:
            return json.dumps({"error": f"Group({name}) not found"})
        groups_info = []
        agents_dict = {}
        for agent_name in backend_group.agent_names:
            agent = AgentService.get_agent(GetAgentModel(name=agent_name))
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
            locked=backend_group.locked
        )
        groups_info.append(group_info.dict(exclude={'agent_names', 'auth'}))
        # Return the JSON representation of the groups info
        return json.dumps({"response": groups_info})

    @staticmethod
    def discover_groups(query: str) -> str:
        from . import BackendService, DiscoverGroupsModel
        response, err = BackendService.discover_backend_groups(DiscoverGroupsModel(query=query))
        if err is not None:
            return err
        return response

    @staticmethod
    def upsert_group(group: str, description: str, agents_to_add: List[str] = None, agents_to_remove: List[str] = None, locked: bool = None) -> str:
        from . import UpsertGroupModel, GetGroupModel, GetAgentModel, AgentService
        backend_group = GroupService.get_group(GetGroupModel(name=group))
        if backend_group:
            if backend_group.locked and (agents_to_add or agents_to_remove or (locked and locked != backend_group.locked) ):
                return json.dumps({"error": f"Group({group}) is locked, agents cannot be added/removed and locked field cannot be modified"})
        else:
            if len(agents_to_add) < 3:
                return json.dumps({"error": f"Could not create group: does not have sufficient agents, at least 3 are needed. Current agents proposed: {', '.join(agents_to_add)}"})
            found_term = False
            for agent_name in agents_to_add:
                agent = AgentService.get_agent(GetAgentModel(name=agent_name))
                if agent is None:
                    return json.dumps({"error": f"Could not get agent: {agent_name}"})
                if agent.capability & TERMINATE:
                    found_term = True
                    break
            if not found_term:
                return json.dumps({"error": f"Could not create group: does not have someone who can TERMINATE the group. Current agents proposed: {', '.join(agents_to_add)}"})
        group_managers, err = GroupService.upsert_groups([UpsertGroupModel(
            name=group,
            description=description,
            agents_to_add=agents_to_add,
            agents_to_remove=agents_to_remove,
            locked=locked
        )])
        if err is not None:
            return err
        return json.dumps({"response": f"Group({group}) upserted!"})

    def start_nested_chat(group: str, message: str) -> str:
        from . import GetGroupModel
        to_group_obj = GroupService.get_group(GetGroupModel(name=group))
        if to_group_obj is None:
            return json.dumps({"error": f"Could not send message: to_group({group}) not found"})
        if GroupService.current_group.nested_chat_completed_event.is_set():
            return json.dumps({"error": "A nested chat from this group is still in progress. Please wait until it's completed."})
        if to_group_obj.nested_chat_completed_event.is_set():
            return json.dumps({"error": "A nested chat in the to_group({to_group}) is still in progress. Please wait until it's completed."})
        if not GroupService.current_group:
           return json.dumps({"error": "No active group chat found."})
        to_group_obj.reset()
        asyncio.create_task(
            GroupService.start_nested_task(
                GroupService.current_group,
                GroupService.current_group.a_initiate_chat,
                GroupService.process_nested_chat_results,
                recipient=to_group_obj,
                message=message
            )
        )
        response = f"Message sent from group ({GroupService.current_group}) to group ({group})! Nested chat started, waiting for completion."
        GroupService.current_group = to_group_obj
        return json.dumps({"response": response})
    
    @staticmethod
    def _create_group(backend_group):
        from . import GetAgentModel, AgentService, MakeService
        group_agents = []
        for agent_name in backend_group.agent_names:
            agent = AgentService.get_agent(GetAgentModel(name=agent_name))
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
                llm_config={"api_key": MakeService.auth.api_key}
            ), None

    @staticmethod
    def update_group(group, backend_group):
        from . import MakeService, AgentService, GetAgentModel
        group.description = backend_group.description
        group.incoming = backend_group.incoming
        group.outgoing = backend_group.outgoing
        group.locked = backend_group.locked
        agent_names = group.agent_names
        for agent_name in backend_group.agent_names:
            if agent_name not in agent_names:
                agent = AgentService.get_agent(GetAgentModel(name=agent_name))
                if agent is None:
                    return None, json.dumps({"error": f"Could not get group agent: {agent_name}"})
                group.groupchat.agents.append(agent)
        MakeService.GROUP_REGISTRY[group.name] = group
        return group, None
    
    @staticmethod
    def make_group(backend_group):
        from . import MakeService
        group, err = GroupService._create_group(backend_group)
        if err is not None:
            return None, err
        group.description = backend_group.description
        group.incoming = backend_group.incoming
        group.outgoing = backend_group.outgoing
        group.locked = backend_group.locked
        MakeService.GROUP_REGISTRY[group.name] = group
        return group, None

    @staticmethod
    def upsert_groups(upsert_models):
        from . import BackendService, GetGroupModel, MakeService, DeleteGroupModel
        # Step 1: Upsert all groups in batch
        err = BackendService.upsert_backend_groups(upsert_models)
        if err and err != json.dumps({"error": "No groups were upserted, no changes found!"}):
            return None, err

        # Step 2: Retrieve all groups from backend in batch
        get_group_models = [GetGroupModel(name=model.name) for model in upsert_models]
        backend_groups, err = BackendService.get_backend_groups(get_group_models)
        if err:
            return None, err
        if len(backend_groups) == 0:
            return None, json.dumps({"error": "Could not fetch groups from backend"})

        # Step 3: Update local group registry
        successful_groups = []
        for backend_group in backend_groups:
            mgr = MakeService.GROUP_REGISTRY.get(backend_group.name)
            if mgr is None:
                mgr, err = GroupService.make_group(backend_group)
                if err is not None:
                    BackendService.delete_groups([DeleteGroupModel(name=backend_group.name)])
                    return None, err
            else:
                mgr, err = GroupService.update_group(mgr, backend_group)
                if err is not None:
                    return None, err
            successful_groups.append(mgr)
        return successful_groups, None
    
    @staticmethod
    def _get_short_group_description(group_name: str) -> str:
        from . import GetGroupModel, GroupService, MakeService
        group = GroupService.get_group(GetGroupModel(name=group_name))
        if group and group.description:
            return MakeService._get_short_description(group.description)
        else:
            return "Description not found"

    @staticmethod
    def _generate_communication_stats_text(group_manager: GroupChatManager) -> str:
        incoming_communications = "\n".join(
            f"- Group Name: {group_name}: {count} message(s), Group Description: {GroupService._get_short_group_description(group_name)}"
            for group_name, count in group_manager.incoming.items()
        )
        outgoing_communications = "\n".join(
            f"- Group Name: {group_name}: {count} message(s), Group Description: {GroupService._get_short_group_description(group_name)}"
            for group_name, count in group_manager.outgoing.items()
        )

        communications = f"""
        GROUP INFORMATION:
        Group Name: {group_manager.name}
        Participating Roles: {group_manager.groupchat._participant_roles()}
        COMMUNICATION STATS:
        Incoming Communications:
        {incoming_communications}
        Outgoing Communications:
        {outgoing_communications}
        """
        return communications.strip()