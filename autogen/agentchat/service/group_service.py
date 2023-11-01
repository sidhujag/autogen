
from .. import ConversableAgent
from typing import List

class GroupService:
    @staticmethod
    def join_group(sender: ConversableAgent, group_chat: str, hello_message: str = None) -> str:
        from .. import GroupChatManager
        from . import BackendService, AgentService, UpsertAgentModel, GetAgentModel
        group_manager = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=group_chat))
        if group_manager is None:
            return "Could not send message: Doesn't exists"
        if not isinstance(group_manager, GroupChatManager):
            return f"Could not send message: {group_chat} is not a group manager"
        result = group_manager.join_group_helper(sender, hello_message)
        if result != "Group joined!":
            return result
        err = BackendService.upsert_backend_agents([UpsertAgentModel(
            auth=sender.auth,
            name=group_chat,
            agents=group_manager.groupchat.agents,
            invitees=group_manager.groupchat.invitees
        )])
        if err is not None:
            return err
        return result

    @staticmethod
    def invite_to_group(sender: ConversableAgent, agent_name: str, group_chat: str, invite_message: str = None) -> str:
        from .. import GroupChatManager
        from . import BackendService, AgentService, UpsertAgentModel, GetAgentModel
        group_manager = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=group_chat))
        if group_manager is None:
            return "Could not invite to group: Group manager doesn't exists"
        if not isinstance(group_manager, GroupChatManager):
            return f"Could not invite to group: {group_chat} is not a group manager"
        agent = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=agent_name))
        if agent is None:
            return "Could not invite to group: Agent doesn't exists"
        result = group_manager.invite_to_group_helper(sender, agent, invite_message)
        if result != "Invite sent!":
            return result
        err = BackendService.upsert_backend_agents([UpsertAgentModel(
            auth=sender.auth,
            name=group_chat,
            invitees=group_manager.groupchat.invitees
        )])
        if err is not None:
            return err
        return result

    @staticmethod
    def create_group(sender: ConversableAgent, group_chat: str, group_description: str, invitees: List[str], system_message: str = None) -> str:
        from . import MakeService, UpsertAgentModel
        # invite the invitees and add yourself as the sole agent in the group
        agents, err = MakeService.upsert_agents([UpsertAgentModel(
            auth=sender.auth,
            name=group_chat,
            description=group_description,
            system_message=system_message,
            invitees=invitees,
            category="groups"
        )])
        if err is not None:
            return f"Could not create group: {err}"
        return "Group created!", agents[0]

    @staticmethod
    def delete_group(sender: ConversableAgent, group_manager) -> str:
        from . import MakeService, BackendService, DeleteAgentModel
        del_group_error = group_manager.delete_group_helper()
        if del_group_error != "":
            return del_group_error
        del MakeService.AGENT_REGISTRY[group_manager.name]
        err = BackendService.delete_backend_agents([DeleteAgentModel(
            auth=sender.auth,
            name=group_manager.name
        )])
        if err is not None:
            return err
        return "Group deleted!"

    @staticmethod
    def leave_group(sender: ConversableAgent, group_chat: str, goodbye_message: str = None) -> str:
        from .. import GroupChatManager
        from . import BackendService, AgentService, UpsertAgentModel, GetAgentModel
        group_manager = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=group_chat))
        if group_manager is None:
            return "Could not leave group: Doesn't exists"
        if not isinstance(group_manager, GroupChatManager):
            return f"Could not leave group: {group_chat} is not a group manager"
        result = group_manager.leave_group_helper(sender, goodbye_message)
        if result != "Group exited!":
            return result
        err = BackendService.upsert_backend_agents([UpsertAgentModel(
            auth=sender.auth,
            name=group_chat,
            agents=group_manager.groupchat.agents
        )])
        if err is not None:
            return err
        return result