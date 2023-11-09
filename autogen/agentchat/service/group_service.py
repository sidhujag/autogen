
from .. import ConversableAgent, GroupChatManager, GroupChat
from typing import List
import json

class GroupService:
    @staticmethod
    def get_group_manager(group_model) -> GroupChatManager:
        from . import BackendService, MakeService
        manager: GroupChatManager = MakeService.GROUP_REGISTRY.get(group_model.name)
        if manager is None:
            backend_group, err = BackendService.get_backend_groups([group_model])
            if err is None and len(backend_group) > 0:
                manager, err = GroupService.make_group(backend_group[0])
                if err is not None:
                    MakeService.GROUP_REGISTRY[group_model.name] = manager
        return manager

    @staticmethod
    def get_group_info(sender: ConversableAgent, group: str) -> str:
        from . import BackendService, GetGroupModel
        if sender is None:
            return "Sender not found"
        backend_groups, err = BackendService.get_backend_groups([GetGroupModel(auth=sender.auth, name=group)])
        if err is not None or len(backend_groups) == 0:
            return f"Could not discover groups: {err}"
        return backend_groups[0].json()
    
    @staticmethod
    def discover_groups(sender: ConversableAgent, query: str) -> str:
        from . import BackendService, DiscoverGroupsModel
        if sender is None:
            return "Sender not found"
        response, err = BackendService.discover_backend_groups(DiscoverGroupsModel(auth=sender.auth, query=query))
        if err is not None:
            return f"Could not discover groups: {err}"
        return response

    @staticmethod
    def upsert_group(sender: ConversableAgent, group: str, description: str, agents_to_add: List[str] = None, agents_to_remove: List[str] = None) -> str:
        from . import UpsertGroupModel
        group_managers, err = GroupService.upsert_groups([UpsertGroupModel(
            auth=sender.auth,
            name=group,
            description=description,
            agents_to_add=agents_to_add,
            agents_to_remove=agents_to_remove,
        )])
        if err is not None:
            return f"Could not update group: {err}", None
        return "Group upserted!"


    @staticmethod
    def terminate_group(sender: ConversableAgent, group: str, response: str) -> str:
        from . import GetGroupModel
        if sender is None:
            return "Could not send message: sender not found"
        group_manager = GroupService.get_group_manager(GetGroupModel(auth=sender.auth, name=group))
        if group_manager is None:
            return "Could not send message: group not found"
        if sender.name not in group_manager.groupchat.agent_names:
            return "Could not send message: Only agents in the group can terminate it"
        if group_manager.delegator:
            group_manager.send(response, group_manager.delegator, request_reply=True)
            group_manager.delegator = None
        return "TERMINATE"

    def send_message_to_group(sender: ConversableAgent, from_group: str, to_group: str, message: str) -> str:
        from . import GetGroupModel, BackendService, UpdateComms
        if sender is None:
            return "Could not send message: sender not found"
        from_group_manager = GroupService.get_group_manager(GetGroupModel(auth=sender.auth, name=from_group))
        if from_group_manager is None:
            return "Could not send message: from_group not found"

        if sender.name not in from_group_manager.groupchat.agent_names:
            return "Could not send message: Only agents in the from_group can send a message to another group"
            
        to_group_manager = GroupService.get_group_manager(GetGroupModel(auth=sender.auth, name=to_group))
        if to_group_manager is None:
            return "Could not send message: to_group not found"
        if to_group_manager.delegator is not None:
            return f"Could not send message: to_group has already been given a task by group: {to_group_manager.delegator.name}. A group can only work on on task at a time. Wait until it concludes."
        if len(to_group_manager.groupchat.agents) < 3:
            return f"Could not send message: to_group does not have sufficient agents, at least 3 are needed. Current agents in group: {', '.join(to_group_manager.groupchat.agent_names)}"
        found_full = False
        for agent in to_group_manager.groupchat.agents:
            if agent.type == "FULL":
                found_full = True
                break
        if not found_full:
            return f"Could not send message: to_group does not have a FULL agent to manage it. Current agents in group: {', '.join(to_group_manager.groupchat.agent_names)}"
            
        # Increment the communication stats
        from_group_manager.outgoing[to_group_manager.name] = from_group_manager.outgoing.get(to_group_manager.name, 0) + 1
        to_group_manager.incoming[from_group_manager.name] = to_group_manager.incoming.get(from_group_manager.name, 0) + 1
        err = BackendService.update_communication_stats(UpdateComms(auth=sender.auth, 
                                                                    sender=from_group_manager.name, 
                                                                    receiver=to_group_manager.name))
        if err:
            return err
        to_group_manager.delegator = from_group_manager
        from_group_manager.send(message, to_group_manager, request_reply=True)
        return "TERMINATE"
    
    @staticmethod
    def _create_group(backend_group) -> GroupChatManager:
        from . import GetAgentModel, AgentService
        group_agents = []
        for agent_name in backend_group.agent_names:
            agent = AgentService.get_agent(GetAgentModel(auth=backend_group.auth, name=agent_name))
            if agent is None:
                return None, f"Could not get group agent: {agent_name}"
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
            )

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
                    return None, f"Could not get group agent: {agent_name}"
                group.groupchat.agents.append(agent)
        MakeService.GROUP_REGISTRY[group.name] = group
    
    @staticmethod
    def make_group(backend_group):
        from . import MakeService
        group = GroupService._create_group(backend_group)
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
        if err and err != "No groups were upserted, no changes found!":
            return None, err

        # Step 2: Retrieve all groups from backend in batch
        get_group_models = [GetGroupModel(auth=model.auth, name=model.name) for model in upsert_models]
        backend_groups, err = BackendService.get_backend_groups(get_group_models)
        if err:
            return None, err
        if len(backend_groups) == 0:
            return None, "Could not fetch groups from backend"

        # Step 3: Update local group registry
        successful_groups = []
        for backend_group in backend_groups:
            mgr = MakeService.GROUP_REGISTRY.get(backend_group.name)
            if mgr is None:
                mgr, err = GroupService.make_group(backend_group)
                if err is not None:
                    return None, err
            else:
                GroupService.update_group(mgr, backend_group)
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