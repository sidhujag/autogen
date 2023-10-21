from dataclasses import dataclass
import sys
from typing import Dict, List, Optional, Union
from .agent import Agent
from .conversable_agent import ConversableAgent
import logging

logger = logging.getLogger(__name__)

GROUP_MANAGER_SYSTEM_MESSAGE = """ As a group manager you should keep sending messages to relevant agents in your group until you are completely satisfied of your answer and result or are waiting on results from other agents. 
As you work step-by-step, when agents complete their tasks you should delegate to the next agent based on your internal plan until all tasks in your group are done at which point you can let the agent that tasked you know of your result by sending them a message.
Note: As soon as you stop sending messages through send_message, the group will stop communicating until a human or another agent else sends a message to you.
"""
@dataclass
class GroupChat:
    """A group chat class that contains the following data fields:
    - agents: a list of participating agents.
    - messages: a list of messages in the group chat.
    - max_round: the maximum number of rounds.
    - admin_name: the name of the admin agent if there is one. Default is "Admin".
        KeyBoardInterrupt will make the admin agent take over.
    - func_call_filter: whether to enforce function call filter. Default is True.
        When set to True and when a message is a function call suggestion,
        the next speaker will be chosen from an agent which contains the corresponding function name
        in its `function_map`.
    """

    agents: List[Agent]
    invitees: List[str]
    messages: List[Dict]
    max_round: int = 10
    admin_name: str = "Admin"
    func_call_filter: bool = True

    @property
    def agent_names(self) -> List[str]:
        """Return the names of the agents in the group chat."""
        return [agent.name for agent in self.agents]

    def reset(self):
        """Reset the group chat."""
        self.messages.clear()

    def agent_by_name(self, name: str) -> Agent:
        """Find the next speaker based on the message."""
        return self.agents[self.agent_names.index(name)]

    def next_agent(self, agent: Agent, agents: List[Agent]) -> Agent:
        """Return the next agent in the list."""
        if agents == self.agents:
            return agents[(self.agent_names.index(agent.name) + 1) % len(agents)]
        else:
            offset = self.agent_names.index(agent.name) + 1
            for i in range(len(self.agents)):
                if self.agents[(offset + i) % len(self.agents)] in agents:
                    return self.agents[(offset + i) % len(self.agents)]

    def select_speaker_msg(self, agents: List[Agent]):
        """Return the message for selecting the next speaker."""
        return f"""You are in a role play game. The following roles are available:
{self._participant_roles()}.

Read the following conversation.
Then select the next role from {[agent.name for agent in agents]} to play. Only return the role."""

    def select_speaker(self, last_speaker: Agent, selector: ConversableAgent):
        """Select the next speaker."""
        if self.func_call_filter and self.messages and "function_call" in self.messages[-1]:
            # find agents with the right function_map which contains the function name
            agents = [
                agent for agent in self.agents if agent.can_execute_function(self.messages[-1]["function_call"]["name"])
            ]
            if len(agents) == 1:
                # only one agent can execute the function
                return agents[0]
            elif not agents:
                # find all the agents with function_map
                agents = [agent for agent in self.agents if agent.function_map]
                if len(agents) == 1:
                    return agents[0]
                elif not agents:
                    raise ValueError(
                        f"No agent can execute the function {self.messages[-1]['name']}. "
                        "Please check the function_map of the agents."
                    )
        else:
            agents = self.agents
            # Warn if GroupChat is underpopulated
            n_agents = len(agents)
            if n_agents < 3:
                logger.warning(
                    f"GroupChat is underpopulated with {n_agents} agents. Direct communication would be more efficient."
                )
        selector.update_system_message(self.select_speaker_msg(agents))
        final, name = selector.generate_oai_reply(
            self.messages
            + [
                {
                    "role": "system",
                    "content": f"Read the above conversation. Then select the next role from {[agent.name for agent in agents]} to play. Only return the role.",
                }
            ]
        )
        if not final:
            # i = self._random.randint(0, len(self._agent_names) - 1)  # randomly pick an id
            return self.next_agent(last_speaker, agents)
        try:
            return self.agent_by_name(name)
        except ValueError:
            return self.next_agent(last_speaker, agents)

    def _participant_roles(self):
        return "\n".join([f"{agent.name}: {agent.system_message}" for agent in self.agents])


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

    def is_agent_in_group(self, agent: ConversableAgent) -> bool:
        return self.groupchat.agents(agent) is not None

    def join_group_helper(self, agent: ConversableAgent, welcome_message: str) -> str:
        if agent.name not in self.groupchat.invitees:
            return "Could not join group: Not invited"
        if self.is_agent_in_group(agent) is True:
            return "Could not join group: Already in the group"
        del self.groupchat.invitees[agent.name]
        other_roles = f"The following other agents are in the group: {self.groupchat._participant_roles()}, the group manager: {self.name}"
        self.groupchat.agents.append(agent)
        # send discovery of other agents to the new agent
        self.send(other_roles, agent, request_reply=False, silent=True)
        if welcome_message:
            agent.send(welcome_message, self, request_reply=False, silent=True)
        new_system_message = self.system_message + f"\nThe following agents are in the group: {self.groupchat._participant_roles()}, the group manager: {self.name}"
        self.update_system_message(new_system_message)
        return "Group joined!"

    def leave_group_helper(self, agent: ConversableAgent, goodbye_message: str = None, **args) -> str:
        if self.is_agent_in_group(agent) is False:
            return "Could not leave group: Not in the group"
        del self.groupchat.agents[agent.name]
        if goodbye_message:
            agent.send(goodbye_message, self, request_reply=False, silent=True)
        new_system_message = self.system_message + f"\nThe following agents are in the group: {self.groupchat._participant_roles()}, the group manager: {self.name}"
        self.update_system_message(new_system_message)
        return "Group exited!"

    def delete_group_helper(self, **args) -> str:
        if len(self.groupchat.agents) > 0:
            return "Could not delete group: Group is not empty"
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
        config.messages.append(message)
        # broadcast the message to all agents except the speaker
        for agent in config.agents:
            if agent != speaker:
                self.send(message, agent, request_reply=False, silent=True)
        return True, None
