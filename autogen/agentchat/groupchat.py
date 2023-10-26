from dataclasses import dataclass
import sys
from typing import Dict, List, Optional, Union
from .agent import Agent
import logging
from . import ConversableAgent
logger = logging.getLogger(__name__)

GROUP_MANAGER_SYSTEM_MESSAGE = """ As a group manager you should keep sending messages to relevant agents in your group until you are completely satisfied of your answer and result or are waiting on results from other agents. 
As you work step-by-step, when agents complete their tasks you should delegate to the next agent based on your internal plan until all tasks in your group are done at which point you can let the agent that tasked you know of your result by sending them a message.
Note: As soon as you stop sending messages through send_message, the group will stop communicating until a human or another agent else sends a message to you.
Every message sent in a group gets copied to every agent in the group. This means the more agents communicating and the more content the bigger the context window requirements and costs for inferencing new messages in the group.
"""
@dataclass
class GroupChat:
    """A group chat class that contains the following data fields:
    - agents: a list of participating agents.
    - invitees: a list of invited agents to join group.
    """

    agents: List[Dict]
    invitees: List[str]
    def reset(self):
        """Reset the group chat."""
        self.agents.clear()
        self.invitees.clear()

    def _participant_roles(self):
        return "\n".join([f"{agent['name']}: {agent['description']}" for agent in self.agents])


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
            system_message=system_message + GROUP_MANAGER_SYSTEM_MESSAGE,
            **kwargs,
        )
        self.register_reply(Agent, GroupChatManager.run_chat, config=groupchat, reset_config=GroupChat.reset)
        # self._random = random.Random(seed)

    def is_agent_in_group(self, agent_name: str) -> bool:
        return any(agent['name'] == agent_name for agent in self.groupchat.agents)

    def join_group_helper(self, agent: ConversableAgent,  welcome_message: str) -> str:
        if agent.name not in self.groupchat.invitees:
            return "Could not join group: Not invited"
        if self.is_agent_in_group(agent.name) is True:
            return "Could not join group: Already in the group"
        try:
            self.groupchat.invitees.remove(agent.name)
        except ValueError:
            return "Could not join group: Not invited"
        other_roles = f"The following other agents are in the group: {self.groupchat._participant_roles()}, the group manager: {self.name}"
        self.groupchat.agents.append({"name": agent.name, "description": agent.description})
        # send discovery of other agents to the new agent
        self.send(other_roles, agent, request_reply=False, silent=True)
        if welcome_message:
            agent.send(welcome_message, self, request_reply=False, silent=True)
        new_system_message = self.system_message + f"\nThe following agents are in the group: {self.groupchat._participant_roles()}, the group manager: {self.name}"
        self.update_system_message(new_system_message)
        return "Group joined!"

    def leave_group_helper(self, agent: ConversableAgent, goodbye_message: str = None, **args) -> str:
        if self.is_agent_in_group(agent.name) is False:
            return "Could not leave group: Not in the group"
        # Find the agent in the agents list
        agent_to_remove = next((a for a in self.groupchat.agents if a['name'] == agent.name), None)
        
        # If the agent is found, remove it from the agents list
        if agent_to_remove:
            self.groupchat.agents.remove(agent_to_remove)
        else:
            return "Could not leave group: Agent not found in group"
        if goodbye_message:
            agent.send(goodbye_message, self, request_reply=False, silent=True)
        new_system_message = self.system_message + f"\nThe following agents are in the group: {self.groupchat._participant_roles()}, the group manager: {self.name}"
        self.update_system_message(new_system_message)
        return "Group exited!"

    def delete_group_helper(self, **args) -> str:
        if len(self.groupchat.agents) > 0:
            return "Could not delete group: Group is not empty"
        self.groupchat.clear()
        del self.groupchat
        return ""

    def invite_to_group_helper(self, inviter: ConversableAgent, invited: ConversableAgent, invite_message: str) -> str:
        if invited.name in self.groupchat.invitees:
            return "Could not invite to group: Already invited"
        if self.is_agent_in_group(invited.name) is True:
            return "Could not invite to group: Already in the group"
        if self.is_agent_in_group(inviter.name) is False:
            return "Cannot invite others to this group: You are not in the group"
        self.groupchat.invitees.append(invited.name)
        if invite_message:
            inviter.send(invite_message, invited, request_reply=False, silent=True)
        return "Invite sent!"
    
    def run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[GroupChat] = None,
    ) -> Union[str, Dict, None]:
        """Run a group chat."""
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        # broadcast the message to all agents except the speaker
        for agent in config.agents:
            if agent != speaker:
                self.send(message, agent, request_reply=False, silent=True)
        # this should be the first callback so let the rest of the callbacks run, at the end AI can reply if it gets there
        return False, None
