from dataclasses import dataclass
import sys
from typing import Dict, List, Optional, Union
from .agent import Agent
from .conversable_agent import ConversableAgent
import logging

logger = logging.getLogger(__name__)


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

    agents: List[str]
    invitees: List[str]
    messages: List[Dict]
    max_round: int = 10
    admin_name: str = "Admin"
    func_call_filter: bool = True


    def reset(self):
        """Reset the group chat."""
        self.messages.clear()
        self.invitees.clear()
        self.agents.clear()

    def agent_by_name(self, name: str) -> str:
        """Find the next speaker based on the message."""
        return self.agents[self.agents.index(name)]

    def next_agent(self, agent: Agent, agents: List[Agent]) -> str:
        """Return the next agent in the list."""
        if agents == self.agents:
            return agents[(self.agents.index(agent.name) + 1) % len(agents)]
        else:
            offset = self.agents.index(agent.name) + 1
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
        return "\n".join([f"{agent.name}: {agent.description}" for agent in self.agents])


class GroupChatManager(ConversableAgent):
    """(In preview) A chat manager agent that can manage a group chat of multiple agents."""

    def __init__(
        self,
        groupchat: GroupChat,
        name: Optional[str] = "chat_manager",
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
        self.groupchat.agents.append(agent.name)
        if welcome_message:
            agent.send(welcome_message, self, request_reply=False, silent=True)
        return "Group joined!"

    def leave_group_helper(self, agent: ConversableAgent, goodbye_message: str = None) -> str:
        if agent.name not in self.groupchat.agents:
            return "Could not leave group: Not in the group"
        self.groupchat.agents.remove(agent.name)
        if goodbye_message:
            agent.send(goodbye_message, self, request_reply=False, silent=True)
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
        groupchat = config
        for i in range(groupchat.max_round):
            # set the name to speaker's name if the role is not function
            if message["role"] != "function":
                message["name"] = speaker.name
            groupchat.messages.append(message)
            # broadcast the message to all agents except the speaker
            for agent_name in groupchat.agents:
                agent = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=agent_name))
                if agent != speaker:
                    self.send(message, agent, request_reply=False, silent=True)
            if i == groupchat.max_round - 1:
                # the last round
                break
            try:
                # select the next speaker
                speaker_name = groupchat.select_speaker(speaker, self)
                speaker = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=speaker_name))
                # let the speaker speak
                reply = speaker.generate_reply(sender=self)
            except KeyboardInterrupt:
                # let the admin agent speak if interrupted
                if groupchat.admin_name in groupchat.agents:
                    # admin agent is one of the participants
                    speaker_name = groupchat.agent_by_name(groupchat.admin_name)
                    speaker = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=speaker_name))
                    reply = speaker.generate_reply(sender=self)
                else:
                    # admin agent is not found in the participants
                    raise
            if reply is None:
                break
            # The speaker sends the message without requesting a reply
            speaker.send(reply, self, request_reply=False)
            message = self.last_message(speaker)
        return True, None

    async def a_run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[GroupChat] = None,
    ):
        """Run a group chat asynchronously."""
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        groupchat = config
        for i in range(groupchat.max_round):
            # set the name to speaker's name if the role is not function
            if message["role"] != "function":
                message["name"] = speaker.name
            groupchat.messages.append(message)
            # broadcast the message to all agents except the speaker
            for agent in groupchat.agents:
                if agent != speaker:
                    await self.a_send(message, agent, request_reply=False, silent=True)
            if i == groupchat.max_round - 1:
                # the last round
                break
            try:
                # select the next speaker
                speaker = groupchat.select_speaker(speaker, self)
                # let the speaker speak
                reply = await speaker.a_generate_reply(sender=self)
            except KeyboardInterrupt:
                # let the admin agent speak if interrupted
                if groupchat.admin_name in groupchat.agents:
                    # admin agent is one of the participants
                    speaker = groupchat.agent_by_name(groupchat.admin_name)
                    reply = await speaker.a_generate_reply(sender=self)
                else:
                    # admin agent is not found in the participants
                    raise
            if reply is None:
                break
            # The speaker sends the message without requesting a reply
            await speaker.a_send(reply, self, request_reply=False)
            message = self.last_message(speaker)
        return True, None