from .conversable_agent import ConversableAgent
from .agent import Agent
from typing import Callable, Dict, Optional, Union, List, Any, Tuple
is_termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()


class DiscoverableConversableAgent(ConversableAgent):
    incoming: Dict[str, Any]
    outgoing: Dict[str, Any]
    """(In preview) A proxy agent for the user, that can execute code and provide feedback to the other agents.

    DiscoverableConversableAgent is a subclass of ConversableAgent configured with `code_execution_config` to False
    By default, the agent will prompt for human input every time a message is received.
    Code execution is enabled by default. LLM-based auto reply is disabled by default.
    To modify auto reply, register a method with [`register_reply`](conversable_agent#register_reply).
    To modify the way to get human input, override `get_human_input` method.
    To modify the way to execute code blocks, single code block, or function call, override `execute_code_blocks`,
    `run_code`, and `execute_function` methods respectively.
    To customize the initial message when a conversation starts, override `generate_init_message` method.
    """

    def __init__(
        self,
        name: str,
        is_termination_msg: Optional[Callable[[Dict], bool]] = is_termination_msg,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[str] = "TERMINATE",
        function_map: Optional[Dict[str, Callable]] = None,
        code_execution_config: Optional[Union[Dict, bool]] = None,
        default_auto_reply: Optional[Union[str, Dict, None]] = "",
        llm_config: Optional[Union[Dict, bool]] = None,
        system_message: Optional[str] = "",
        incoming: Dict[str, Any] = {},
        outgoing: Dict[str, Any] = {},
        
    ):
        """
        Args:
            name (str): name of the agent.
            is_termination_msg (function): a function that takes a message in the form of a dictionary
                and returns a boolean value indicating if this received message is a termination message.
                The dict can contain the following keys: "content", "role", "name", "function_call".
            max_consecutive_auto_reply (int): the maximum number of consecutive auto replies.
                default to None (no limit provided, class attribute MAX_CONSECUTIVE_AUTO_REPLY will be used as the limit in this case).
                The limit only plays a role when human_input_mode is not "ALWAYS".
            human_input_mode (str): whether to ask for human inputs every time a message is received.
                Possible values are "ALWAYS", "TERMINATE", "NEVER".
                (1) When "ALWAYS", the agent prompts for human input every time a message is received.
                    Under this mode, the conversation stops when the human input is "exit",
                    or when is_termination_msg is True and there is no human input.
                (2) When "TERMINATE", the agent only prompts for human input only when a termination message is received or
                    the number of auto reply reaches the max_consecutive_auto_reply.
                (3) When "NEVER", the agent will never prompt for human input. Under this mode, the conversation stops
                    when the number of auto reply reaches the max_consecutive_auto_reply or when is_termination_msg is True.
            function_map (dict[str, callable]): Mapping function names (passed to openai) to callable functions.
            code_execution_config (dict or False): config for the code execution.
                To disable code execution, set to False. Otherwise, set to a dictionary with the following keys:
                - work_dir (Optional, str): The working directory for the code execution.
                    If None, a default working directory will be used.
                    The default working directory is the "extensions" directory under
                    "path_to_autogen".
                - use_docker (Optional, list, str or bool): The docker image to use for code execution.
                    If a list or a str of image name(s) is provided, the code will be executed in a docker container
                    with the first image successfully pulled.
                    If None, False or empty, the code will be executed in the current environment.
                    Default is True, which will be converted into a list.
                    If the code is executed in the current environment,
                    the code must be trusted.
                - timeout (Optional, int): The maximum execution time in seconds.
                - last_n_messages (Experimental, Optional, int): The number of messages to look back for code execution. Default to 1.
            default_auto_reply (str or dict or None): the default auto reply message when no code execution or llm based reply is generated.
            llm_config (dict or False): llm inference configuration.
                Please refer to [Completion.create](/docs/reference/oai/completion#create)
                for available options.
                Default to false, which disables llm-based auto reply.
            system_message (str): system message for ChatCompletion inference.
                Only used when llm_config is not False. Use it to reprogram the agent.
        """
        super().__init__(
            name,
            system_message,
            is_termination_msg,
            max_consecutive_auto_reply,
            human_input_mode,
            function_map,
            code_execution_config,
            llm_config,
            default_auto_reply,
        )
        self.register_reply([Agent, None], DiscoverableConversableAgent.generate_stats_reply)
        self.incoming = incoming
        self.outgoing = outgoing
        
    def generate_stats_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional["DiscoverableConversableAgent"] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        from .service import MakeService, BackendService, UpdateComms, AgentStats
        """In this function, we will update the context and reset the conversation based on different conditions.
        We'll update the context and reset the conversation if update_context is True and either of the following:
        (1) the last message contains "UPDATE CONTEXT",
        (2) the last message doesn't contain "UPDATE CONTEXT" and the customized_answer_prefix is not in the message.
        """
        sender_description=sender.description[:100]
        receiver_description=self.description[:100]
        if self.name in sender.outgoing:
            sender.outgoing[self.name].count += 1
        else:
            sender.outgoing[self.name] = AgentStats(count=1, description=sender_description)
        
        # Optimize updating the incoming count for this agent
        if sender.name in self.incoming:
            self.incoming[sender.name].count += 1
        else:
            self.incoming[sender.name] = AgentStats(count=1, description=receiver_description)
    
        err = BackendService.update_communication_stats(UpdateComms(auth=sender.auth, 
                                                                    sender=sender.name, 
                                                                    receiver=self.name,
                                                                    sender_description=sender_description,
                                                                    receiver_description=receiver_description))
        if err:
            return False, err
        MakeService.update_system_message(self)
        MakeService.update_system_message(sender)
        return False, None