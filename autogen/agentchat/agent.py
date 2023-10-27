from typing import Dict, List, Optional, Union


class Agent:
    """(In preview) An abstract class for AI agent.

    An agent can communicate with other agents and perform actions.
    Different agents can differ in what actions they perform in the `receive` method.
    """

    def __init__(
        self,
        name: str,
        description: str,
        api_key: str,
        user_id: str
    ):
        """
        Args:
            name (str): name of the agent.
        """
        # a dictionary of conversations, default value is list
        self._name = name
        self._description = description
        self._api_key = api_key
        self._user_id = user_id

    @property
    def name(self):
        """Get the name of the agent."""
        return self._name

    @property
    def description(self):
        """Get the description of the agent."""
        return self._description
    
    @description.setter
    def description(self, value):
        """Set the description of the agent."""
        self._description = value

    @property
    def api_key(self):
        """Get the api_key of the agent."""
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        """Set the api_key of the agent."""
        self._api_key = value
       
    @property
    def user_id(self):
        """Get the user_id of the agent (for namespacing)."""
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        """Set the user_id of the agent."""
        self._user_id = value

    def send(self, message: Union[Dict, str], recipient: "Agent", request_reply: Optional[bool] = None):
        """(Abstract method) Send a message to another agent."""

    async def a_send(self, message: Union[Dict, str], recipient: "Agent", request_reply: Optional[bool] = None):
        """(Abstract async method) Send a message to another agent."""

    def receive(self, message: Union[Dict, str], sender: "Agent", request_reply: Optional[bool] = None):
        """(Abstract method) Receive a message from another agent."""

    async def a_receive(self, message: Union[Dict, str], sender: "Agent", request_reply: Optional[bool] = None):
        """(Abstract async method) Receive a message from another agent."""

    def reset(self):
        """(Abstract method) Reset the agent."""

    def generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional["Agent"] = None,
        **kwargs,
    ) -> Union[str, Dict, None]:
        """(Abstract method) Generate a reply based on the received messages.

        Args:
            messages (list[dict]): a list of messages received.
            sender: sender of an Agent instance.
        Returns:
            str or dict or None: the generated reply. If None, no reply is generated.
        """

    async def a_generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional["Agent"] = None,
        **kwargs,
    ) -> Union[str, Dict, None]:
        """(Abstract async method) Generate a reply based on the received messages.

        Args:
            messages (list[dict]): a list of messages received.
            sender: sender of an Agent instance.
        Returns:
            str or dict or None: the generated reply. If None, no reply is generated.
        """
