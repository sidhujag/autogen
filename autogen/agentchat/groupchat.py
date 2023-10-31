from dataclasses import dataclass
import sys
from typing import Dict, List, Optional, Union
from .agent import Agent
import logging
from . import ConversableAgent
logger = logging.getLogger(__name__)

@dataclass
class GroupChat:
    """A group chat class that contains the following data fields:
    - agents: a list of participating agents.
    - invitees: a list of invited agents to join group.
    """

    agents: List[str]
    invitees: List[str]
    def reset(self):
        """Reset the group chat."""
        self.agents = []
        self.invitees = []

class GroupChatManager(ConversableAgent):
    """(In preview) A chat manager agent that can manage a group chat of multiple agents."""

    def __init__(
        self,
        groupchat: GroupChat,
        name: Optional[str] = "group_manager",
        # unlimited consecutive auto reply by default
        max_consecutive_auto_reply: Optional[int] = sys.maxsize,
        human_input_mode: Optional[str] = "NEVER",
        system_message: Optional[str] = "Group chat manager.",
        # seed: Optional[int] = 4,
        **kwargs,
    ):
        super().__init__(
            name=name,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            system_message=system_message,
            **kwargs,
        )
        self.base_system_message = system_message
        self.groupchat = groupchat
        # Order of register_reply is important.
        # Allow sync chat if initiated using initiate_chat
        self.register_reply(Agent, GroupChatManager.run_chat, config=groupchat, reset_config=GroupChat.reset)
        # Allow async chat if initiated using a_initiate_chat
        self.register_reply(Agent, GroupChatManager.a_run_chat, config=groupchat, reset_config=GroupChat.reset)

        # self._random = random.Random(seed)

    
    def join_group_helper(self, agent: ConversableAgent, welcome_message: str = None) -> str:
        if agent.name in self.groupchat.agents:
            return "Could not join group: Already in the group"
        if agent.name not in self.groupchat.invitees:
            return "Could not join group: Not invited"
        if agent.name == self.name:
            return "Could not join group: You are the group manager already"
        self.groupchat.invitees.remove(agent.name)
        other_roles = f"The following other agents are in the group: {', '.join(self.groupchat.agents)}, the group manager: {self.name}"
        self.groupchat.agents.append(agent.name)
        self.send(other_roles, agent, request_reply=False, silent=True)
        if welcome_message:
            agent.send(welcome_message, self, request_reply=False, silent=True)
        self.update_system_message(self.base_system_message + f"\nThe following agents are in the group: {', '.join(self.groupchat.agents)}, the group manager: {self.name}")
        return "Group joined!"

    def leave_group_helper(self, agent: ConversableAgent, goodbye_message: str = None) -> str:
        if agent.name not in self.groupchat.agents:
            return "Could not leave group: Not in the group"
        self.groupchat.agents.remove(agent.name)
        if goodbye_message:
            agent.send(goodbye_message, self, request_reply=False, silent=True)
        self.update_system_message(self.base_system_message + f"\nThe following agents are in the group: {', '.join(self.groupchat.agents)}, the group manager: {self.name}")
        return "Group exited!"

    def invite_to_group_helper(self, inviter: ConversableAgent, invited: ConversableAgent, invite_message: str = None) -> str:
        if invited.name in self.groupchat.invitees:
            return "Could not invite to group: Already invited"
        if invited.name in self.groupchat.agents:
            return "Could not invite to group: Already in the group"
        if inviter.name not in self.groupchat.agents and inviter.name != self.name:
            return "Cannot invite others to this group: You are not in the group"
        if invited.name == self.name:
            return "Could not invite to group: You are the group manager already"
        self.groupchat.invitees.append(invited.name)
        if invite_message:
            inviter.send(invite_message, invited, request_reply=False, silent=True)
        return "Invite sent!"

    def delete_group_helper(self) -> str:
        if len(self.groupchat.agents) > 0:
            return "Could not delete group: Group is not empty"
        self.groupchat.clear()
        return ""

    def run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[GroupChat] = None,
    ) -> Union[str, Dict, None]:
        """Run a group chat."""
        from .service import AgentService, GetAgentModel
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        # broadcast the message to all agents except the speaker
        for agent_name in config.agents:
            agent = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=agent_name))
            if agent and agent != speaker:
                self.send(message, agent, request_reply=False, silent=True)
        # this should be the first callback so let the rest of the callbacks run, at the end AI can reply if it gets there
        return False, None


    async def a_run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[GroupChat] = None,
    ):
        """Run a group chat asynchronously."""
        from .service import AgentService, GetAgentModel
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        for agent_name in config.agents:
            agent = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=agent_name))
            if agent and agent != speaker:
                 await self.a_send(message, agent, request_reply=False, silent=True)
        return True, None