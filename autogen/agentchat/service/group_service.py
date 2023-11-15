
from .. import GroupChatManager, GroupChat
from ..contrib.gpt_assistant_agent import GPTAssistantAgent
from typing import List
import json
GROUP_INFO = 1
CODE_INTERPRETER_TOOL = 2
RETRIEVAL_TOOL = 4
FILES = 8
MANAGEMENT = 16

class GroupService:
    @staticmethod
    def get_group_manager(group_model) -> GroupChatManager:
        from . import BackendService, MakeService
        manager: GroupChatManager = MakeService.GROUP_REGISTRY.get(group_model.name)
        if manager is None:
            backend_groups, err = BackendService.get_backend_groups([group_model])
            if err is None and len(backend_groups) > 0:
                manager, err = GroupService.make_group(backend_groups[0])
                if err is not None:
                    MakeService.GROUP_REGISTRY[group_model.name] = manager
        return manager
    
    @staticmethod
    def get_group_info(sender: GPTAssistantAgent, group: str) -> str:
        from . import BackendService, GetGroupModel, GroupInfo, AgentService, MakeService, GetAgentModel
        if sender is None:
            return json.dumps({"error": "Sender not found"})

        backend_groups, err = BackendService.get_backend_groups([GetGroupModel(auth=sender.auth, name=group)])
        if err is not None or not backend_groups:
            return json.dumps({"error": str(err) if err else "No groups found"})
        groups_info = []
        for backend_group in backend_groups:
            agents_dict = {}
            for agent_name in backend_group.agent_names:
                agent = AgentService.get_agent(GetAgentModel(auth=backend_group.auth, name=agent_name))
                if agent is None:
                    return json.dumps({"error": f"Could not get group agent: {agent_name}"})

                short_description = MakeService._get_short_description(agent.description)
                capability_names = AgentService.get_capability_names(agent.capability)
                capability_text = ", ".join(capability_names) if capability_names else "No capabilities"
                agents_dict[agent.name] = {
                    "capabilities": capability_text,
                    "description": short_description,
                    "files": agent.files
                }
            group_info = GroupInfo(**backend_group.dict(), agents=agents_dict)
            groups_info.append(group_info.dict(exclude={'agent_names'}))

        # Return the JSON representation of the groups info
        return json.dumps(groups_info)


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
    def upsert_group(sender: GPTAssistantAgent, group: str, description: str, agents_to_add: List[str] = None, agents_to_remove: List[str] = None) -> str:
        from . import UpsertGroupModel
        group_managers, err = GroupService.upsert_groups([UpsertGroupModel(
            auth=sender.auth,
            name=group,
            description=description,
            agents_to_add=agents_to_add,
            agents_to_remove=agents_to_remove,
        )])
        if err is not None:
            return err
        return json.dumps({"response": "Group upserted!"})


    @staticmethod
    def terminate_group(sender: GPTAssistantAgent, group: str, response: str) -> str:
        from . import GetGroupModel
        if sender is None:
            return json.dumps({"error": "Could not send message: sender not found"})
        group_manager = GroupService.get_group_manager(GetGroupModel(auth=sender.auth, name=group))
        if group_manager is None:
            return json.dumps({"error": "Could not send message: group not found"})
        if group_manager.dependent:
            group_manager.send(response, group_manager.dependent, request_reply=False)
        group_manager.exiting = True
        return json.dumps({"response": "Group terminating!"})

    def send_message_to_group(sender: GPTAssistantAgent, from_group: str, to_group: str, message: str) -> str:
        from . import GetGroupModel, BackendService, UpdateComms
        if sender is None:
            return json.dumps({"error": "Could not send message: sender not found"})
        if from_group == to_group:
            return json.dumps({"error": "Could not send message: cannot send message to the same group you are sending from"})
        from_group_manager = GroupService.get_group_manager(GetGroupModel(auth=sender.auth, name=from_group))
        if from_group_manager is None:
            return json.dumps({"error": "Could not send message: from_group not found"})
        to_group_manager = GroupService.get_group_manager(GetGroupModel(auth=sender.auth, name=to_group))
        if to_group_manager is None:
            return json.dumps({"error": "Could not send message: to_group not found"})
        if to_group_manager.dependent:
            return json.dumps({"error": f"Could not send message: to_group already depends on a task from {to_group_manager.dependent.name}."})
        if from_group_manager.dependent and to_group == from_group_manager.dependent.name:
            return json.dumps({"error": "Could not send message: cannot send message to the group that assigned a task to you."})
        if len(to_group_manager.groupchat.agents) < 3:
            return json.dumps({"error": f"Could not send message: to_group does not have sufficient agents, at least 3 are needed. Current agents in group: {', '.join(to_group_manager.groupchat.agent_names)}"})
        found_mgr = False
        for agent in to_group_manager.groupchat.agents:
            if agent.capability & MANAGEMENT:
                found_mgr = True
                break
        if not found_mgr:
            return json.dumps({"error": f"Could not send message: to_group does not have a MANAGER. Current agents in group: {', '.join(to_group_manager.groupchat.agent_names)}"})
        # Increment the communication stats
        from_group_manager.outgoing[to_group_manager.name] = from_group_manager.outgoing.get(to_group_manager.name, 0) + 1
        to_group_manager.incoming[from_group_manager.name] = to_group_manager.incoming.get(from_group_manager.name, 0) + 1
        err = BackendService.update_communication_stats(UpdateComms(auth=sender.auth, 
                                                                    sender=from_group_manager.name, 
                                                                    receiver=to_group_manager.name))
        if err:
            return err
        to_group_manager.dependent = from_group_manager
        from_group_manager.tasking = to_group_manager
        from_group_manager.tasking_message = message
        return json.dumps({"response": "Message sent!"})
    
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
        agent_names = group.groupchat.agent_names
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
        manager = GroupService.get_group_manager(GetGroupModel(name=group_name, auth=auth))
        if manager and manager.description:
            return MakeService._get_short_description(manager.description)
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