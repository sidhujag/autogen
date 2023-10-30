
from . import GroupChatManager, MakeService, BackendService, AgentService, ConversableAgent, UpsertAgentModel, DeleteAgentModel, GetAgentModel

class GroupService:
    @staticmethod
    def join_group(sender: ConversableAgent, group_manager_name: str, hello_message: str = None) -> str:
        group_manager = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=group_manager_name))
        if group_manager is None:
            return "Could not send message: Doesn't exists"
        if not isinstance(group_manager, GroupChatManager):
            return f"Could not send message: {group_manager_name} is not a group manager"
        result = group_manager.join_group_helper(sender, hello_message)
        if result != "Group joined!":
            return result
        err = BackendService.upsert_backend_agent(UpsertAgentModel(
            auth=sender.auth,
            name=group_manager_name,
            agents=group_manager.groupchat.agents,
            invitees=group_manager.groupchat.invitees
        ))
        if err is not None:
            return err
        return result

    @staticmethod
    def invite_to_group(sender: ConversableAgent, agent_name: str, group_manager_name: str, invite_message: str = None) -> str:
        group_manager = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=group_manager_name))
        if group_manager is None:
            return "Could not invite to group: Group manager doesn't exists"
        if not isinstance(group_manager, GroupChatManager):
            return f"Could not invite to group: {group_manager_name} is not a group manager"
        agent = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=agent_name))
        if agent is None:
            return "Could not invite to group: Agent doesn't exists"
        result = group_manager.invite_to_group_helper(sender, agent, invite_message)
        if result != "Invite sent!":
            return result
        err = BackendService.upsert_backend_agent(UpsertAgentModel(
            auth=sender.auth,
            name=group_manager_name,
            invitees=group_manager.groupchat.invitees
        ))
        if err is not None:
            return err
        return result

    @staticmethod
    def create_group(sender: ConversableAgent, group_manager_name: str, group_description: str, system_message: str = None) -> str:
        err = MakeService.upsert_agent(sender, UpsertAgentModel(
            auth=sender.auth,
            name=group_manager_name,
            description=group_description,
            system_message=system_message,
            category="groups"
        ))
        if err is not None:
            return f"Could not create group: {err}"
        return "Group created!"

    @staticmethod
    def delete_group(sender: ConversableAgent, group_manager: GroupChatManager) -> str:
        del_group_error = group_manager.delete_group_helper()
        if del_group_error != "":
            return del_group_error
        del MakeService.AGENT_REGISTRY[group_manager.name]
        err = BackendService.delete_backend_agent(DeleteAgentModel(
            auth=sender.auth,
            name=group_manager.name
        ))
        if err is not None:
            return err
        return "Group deleted!"

    @staticmethod
    def leave_group(sender: ConversableAgent, group_manager_name: str, goodbye_message: str = None) -> str:
        group_manager = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=group_manager_name))
        if group_manager is None:
            return "Could not leave group: Doesn't exists"
        if not isinstance(group_manager, GroupChatManager):
            return f"Could not leave group: {group_manager_name} is not a group manager"
        result = group_manager.leave_group_helper(sender, goodbye_message)
        if result != "Group exited!":
            return result
        if len(group_manager.groupchat.agents) == 0:
             result = GroupService.delete_group(sender, group_manager)
             if result != "Group deleted!":
                return result
        err = BackendService.upsert_backend_agent(UpsertAgentModel(
            auth=sender.auth,
            name=group_manager_name,
            agents=group_manager.groupchat.agents
        ))
        if err is not None:
            return err
        return result