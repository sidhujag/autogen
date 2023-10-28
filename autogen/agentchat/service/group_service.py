
from .. import GroupChatManager, MakeService, BackendService, AgentService, ConversableAgent
from backend_service import UpsertAgentModel, DeleteAgentModel

class GroupService:
    def join_group(self, sender: ConversableAgent, group_manager_name: str, hello_message: str = None) -> str:
        group_manager = AgentService.get_agent(group_manager_name)
        if not isinstance(group_manager, GroupChatManager):
            return "Could not send message: group_manager_name is not a group manager"
        if group_manager is None:
            return "Could not send message: Doesn't exists"
        result = group_manager.join_group_helper(sender, hello_message)
        if result != "Group joined!":
            return result
        response, err = BackendService.upsert_agent_data(sender, UpsertAgentModel(
            name=group_manager_name,
            agents=group_manager.groupchat.agents,
            invitees=group_manager.groupchat.invitees
        ))
        if err is not None:
            return err
        return result
   
    def invite_to_group(self, sender: ConversableAgent, agent_name: str, group_manager_name: str, invite_message: str = None) -> str:
        group_manager = AgentService.get_agent(group_manager_name)
        if group_manager is None:
            return "Could not invite to group: Doesn't exists"
        if not isinstance(group_manager, GroupChatManager):
            return "Could not invite to group: group_manager_name is not a group manager"
        agent = AgentService.get_agent(agent_name)
        result = group_manager.invite_to_group_helper(sender, agent, invite_message)
        if result != "Invite sent!":
            return result
        response, err = BackendService.upsert_agent_data(sender, UpsertAgentModel(
            name=group_manager_name,
            invitees=group_manager.groupchat.invitees
        ))
        if err is not None:
            return err
        return result

    def create_group(self, sender: ConversableAgent, group_manager_name: str, group_description: str, system_message: str = None) -> str:
        response, err = MakeService.upsert_agent(sender, UpsertAgentModel(
            name=group_manager_name,
            description=group_description,
            system_message=system_message,
            category="groups"
        ), group_manager_name)
        if err is not None:
            return f"Could not create group: {err}"
        return "Group created!"

    def delete_group(self, sender: ConversableAgent, group_manager: GroupChatManager) -> str:
        del_group_error = group_manager.delete_group_helper()
        if del_group_error != "":
            return del_group_error
        del MakeService.AGENT_REGISTRY[group_manager.name]
        response, err = BackendService.delete_agent(sender, DeleteAgentModel(
            name=group_manager.name
        ))
        if err is not None:
            return err
        return "Group deleted!"

    def leave_group(self, sender: ConversableAgent, group_manager_name: str, goodbye_message: str = None) -> str:
        group_manager = AgentService.get_agent(group_manager_name)
        if group_manager is None:
            return "Could not leave group: Doesn't exists"
        if not isinstance(group_manager, GroupChatManager):
            return "Could not leave group: group_manager_name is not a group manager"
        result = group_manager.leave_group_helper(sender, goodbye_message)
        if result != "Group exited!":
            return result
        if len(group_manager.groupchat.agents) == 0:
             result = self.delete_group(sender, group_manager)
             if result != "Group deleted!":
                return result
        response, err = BackendService.upsert_agent_data(sender, UpsertAgentModel(
            name=group_manager_name,
            agents=group_manager.groupchat.agents
        ))
        if err is not None:
            return err
        return result