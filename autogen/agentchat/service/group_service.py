
from .. import GroupChatManager, GroupChat
from ..contrib.gpt_assistant_agent import GPTAssistantAgent
from typing import List
import json
INFO = 1
TERMINATE = 2
OPENAI_CODE_INTERPRETER = 4
CODING_ASSISTANCE = 8
FUNCTION_CODER = 16
FUNCTION_CODER = 16
OPENAI_RETRIEVAL = 32
OPENAI_FILES = 64
MANAGEMENT = 128

class GroupService:
    @staticmethod
    def get_group(group_model) -> GroupChatManager:
        from . import BackendService, MakeService
        group: GroupChatManager = MakeService.GROUP_REGISTRY.get(group_model.name)
        if group is None:
            backend_groups, err = BackendService.get_backend_groups([group_model])
            if err is None and backend_groups:
                group, err = GroupService.make_group(backend_groups[0])
                if err is None and group:
                    MakeService.GROUP_REGISTRY[group_model.name] = group
        return group
    
    @staticmethod
    def get_group_info(sender: GPTAssistantAgent, name: str, full_description: bool = False) -> str:
        from . import GetGroupModel, GroupInfo, AgentService, MakeService, GetAgentModel
        if sender is None:
            return json.dumps({"error": "Sender not found"})
        backend_group = GroupService.get_group(GetGroupModel(auth=sender.auth, name=name))
        if not backend_group:
            return json.dumps({"error": f"Group({name}) not found"})
        groups_info = []
        agents_dict = {}
        for agent_name in backend_group.agent_names:
            agent = AgentService.get_agent(GetAgentModel(auth=backend_group.auth, name=agent_name))
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
            auth=backend_group.auth,
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
    def discover_groups(sender: GPTAssistantAgent, query: str) -> str:
        from . import BackendService, DiscoverGroupsModel
        if sender is None:
            return json.dumps({"error": "Sender not found"})
        response, err = BackendService.discover_backend_groups(DiscoverGroupsModel(auth=sender.auth, query=query))
        if err is not None:
            return err
        return response

    @staticmethod
    def upsert_group(sender: GPTAssistantAgent, group: str, description: str, agents_to_add: List[str] = None, agents_to_remove: List[str] = None, locked: bool = None) -> str:
        from . import UpsertGroupModel, GetGroupModel, GetAgentModel, AgentService
        backend_group = GroupService.get_group(GetGroupModel(auth=sender.auth, name=group))
        if backend_group:
            if backend_group.locked and (agents_to_add or agents_to_remove or (locked and locked != backend_group.locked) ):
                return json.dumps({"error": f"Group({group}) is locked, agents cannot be added/removed and locked field cannot be modified"})
        else:
            if len(agents_to_add) < 3:
                return json.dumps({"error": f"Could not create group: does not have sufficient agents, at least 3 are needed. Current agents proposed: {', '.join(agents_to_add)}"})
            found_term = False
            for agent_name in agents_to_add:
                agent = AgentService.get_agent(GetAgentModel(auth=backend_group.auth, name=agent_name))
                if agent is None:
                    return json.dumps({"error": f"Could not get agent: {agent_name}"})
                if agent.capability & TERMINATE:
                    found_term = True
                    break
            if not found_term:
                return json.dumps({"error": f"Could not create group: does not have someone who can TERMINATE the group. Current agents proposed: {', '.join(agents_to_add)}"})
        group_managers, err = GroupService.upsert_groups([UpsertGroupModel(
            auth=sender.auth,
            name=group,
            description=description,
            agents_to_add=agents_to_add,
            agents_to_remove=agents_to_remove,
            locked=locked
        )])
        if err is not None:
            return err
        return json.dumps({"response": f"Group({group}) upserted!"})


    @staticmethod
    def terminate_group(sender: GPTAssistantAgent, group: str, rating: int) -> str:
        from . import GetGroupModel, BackendService, UpdateComms
        if sender is None:
            return json.dumps({"error": "Could not send message: sender not found"})
        group_obj = GroupService.get_group(GetGroupModel(auth=sender.auth, name=group))
        if group_obj is None:
            return json.dumps({"error": f"Could not send message: group({group}) not found"})
        if not group_obj.running:
            return json.dumps({"error": f"Could not terminate group({group}): group is currently not running, perhaps already terminated."})

        if group_obj.dependent:
            group_obj.dependent.exit_response = group_obj.last_message(sender)
            if rating >= 7:
                # Increment the communication stats
                group_obj.dependent.outgoing[group_obj.name] = group_obj.dependent.outgoing.get(group_obj.name, 0) + 1
                group_obj.incoming[group_obj.dependent.name] = group_obj.incoming.get(group_obj.dependent.name, 0) + 1
                err = BackendService.update_communication_stats(UpdateComms(auth=sender.auth, 
                                                                            sender=group_obj.dependent.name, 
                                                                            receiver=group_obj.name))
                if err:
                    return err
            group_obj.dependent.running = True
        group_obj.exiting = True
        group_obj.running = False
        return json.dumps({"response": f"Group({group}) terminating!"})

    def send_message_to_group(sender: GPTAssistantAgent, from_group: str, to_group: str, message: str) -> str:
        from . import GetGroupModel
        if sender is None:
            return json.dumps({"error": "Could not send message: sender not found"})
        if from_group == to_group:
            return json.dumps({"error": "Could not send message: cannot send message to the same group you are sending from"})
        from_group_obj = GroupService.get_group(GetGroupModel(auth=sender.auth, name=from_group))
        if from_group_obj is None:
            return json.dumps({"error": f"Could not send message: from_group({from_group}) not found"})
        if not from_group_obj.running:
            return json.dumps({"error": f"Could not send message: from_group({from_group}) is not running"})
        to_group_obj = GroupService.get_group(GetGroupModel(auth=sender.auth, name=to_group))
        if to_group_obj is None:
            return json.dumps({"error": f"Could not send message: to_group({to_group}) not found"})
        if to_group_obj.running:
            return json.dumps({"error": f"Could not send message: to_group({to_group}) is already running"})
        if to_group_obj.dependent:
            return json.dumps({"error": f"Could not send message: to_group({to_group}) already depends on a task from {to_group_obj.dependent.name}."})
        if from_group_obj.dependent and to_group == from_group_obj.dependent.name:
            return json.dumps({"error": "Could not send message: cannot send message to the group that assigned a task to you."})
        to_group_obj.dependent = from_group_obj
        from_group_obj.tasking = to_group_obj
        from_group_obj.running = False
        to_group_obj.running = True
        from_group_obj.tasking_message = f'{sender.name} (to {to_group}):\n{message}'
        return json.dumps({"response": f"Message sent from group ({from_group}) to group ({to_group})!"})
    
    @staticmethod
    def _create_group(backend_group):
        from . import GetAgentModel, AgentService
        group_agents = []
        for agent_name in backend_group.agent_names:
            agent = AgentService.get_agent(GetAgentModel(auth=backend_group.auth, name=agent_name))
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
                llm_config={"api_key": backend_group.auth.api_key}
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
                agent = AgentService.get_agent(GetAgentModel(auth=backend_group.auth, name=agent_name))
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
        group.auth = backend_group.auth
        MakeService.GROUP_REGISTRY[group.name] = group
        return group, None

    @staticmethod
    def upsert_groups(upsert_models):
        from . import BackendService, GetGroupModel, MakeService
        # Step 1: Upsert all groups in batch
        err = BackendService.upsert_backend_groups(upsert_models)
        if err and err != json.dumps({"error": "No groups were upserted, no changes found!"}):
            return None, err

        # Step 2: Retrieve all groups from backend in batch
        get_group_models = [GetGroupModel(auth=model.auth, name=model.name) for model in upsert_models]
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
                    return None, err
            else:
                mgr, err = GroupService.update_group(mgr, backend_group)
                if err is not None:
                    return None, err
            successful_groups.append(mgr)
        return successful_groups, None
    
    @staticmethod
    def _get_short_group_description(group_name: str, auth) -> str:
        from . import GetGroupModel, GroupService, MakeService
        group = GroupService.get_group(GetGroupModel(name=group_name, auth=auth))
        if group and group.description:
            return MakeService._get_short_description(group.description)
        else:
            return "Description not found"

    @staticmethod
    def _generate_communication_stats_text(group_manager: GroupChatManager) -> str:
        incoming_communications = "\n".join(
            f"- Group Name: {group_name}: {count} message(s), Group Description: {GroupService._get_short_group_description(group_name, group_manager.auth)}"
            for group_name, count in group_manager.incoming.items()
        )
        outgoing_communications = "\n".join(
            f"- Group Name: {group_name}: {count} message(s), Group Description: {GroupService._get_short_group_description(group_name, group_manager.auth)}"
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