import os
import copy
from typing import List, Optional, Union, Dict

from requests import Session

import autogen
from .datamodel import AgentConfig, AgentFlowSpec, AgentWorkFlowConfig, Message, SocketMessage
from .utils import get_skills_from_prompt, clear_folder, sanitize_model
from datetime import datetime
from pathlib import Path

class AutoGenWorkFlowManager:
    """
    AutoGenWorkFlowManager class to load agents from a provided configuration and run a chat between them
    """

    def __init__(
        self,
        config: AgentWorkFlowConfig,
        work_dir: str = None,
        clear_work_dir: bool = True,
        session_id: str = "",
        send_message_function: Optional[callable] = None,
        connection_id: Optional[str] = None,
    ) -> None:
        """
        Initializes the AutoGenFlow with agents specified in the config and optional
        message history.

        Args:
            config: The configuration settings for the sender and receiver agents.
            history: An optional list of previous messages to populate the agents' history.

        """
        self.send_message_function = send_message_function
        self.connection_id = connection_id
        self.work_dir = work_dir or "work_dir"
        if clear_work_dir:
            clear_folder(self.work_dir)
        self.config = config
        # given the config, return an AutoGen agent object
        self.sender = self.load(config.sender, session_id)
        self.receiver = self.load(config.receiver, session_id)

        self.agent_history = []

    async def a_process_message_before_send(self, sender: autogen.ConversableAgent, message: Union[Dict, str], recipient: autogen.ConversableAgent, silent: bool):
        if silent:
            return message
        message_internal = sender._message_to_dict(message).copy()
        if "role" not in message_internal:
            message_internal["role"] = "user"
        sender = sender.name
        recipient = recipient.name
        if "name" in message_internal:
            sender = message_internal["name"]
        # if sender is group chat, get summary if summary is set because that means a convo has completed and is returning to you
        message_payload = {
            "recipient": recipient,
            "sender": sender,
            "message": message_internal,
            "timestamp": datetime.now().isoformat(),
        }
        self.agent_history.append(message_payload)  # add to history
        if self.send_message_function:  # send over the message queue
            socket_msg = SocketMessage(
                type="agent_message", data=message_payload, connection_id=self.connection_id)
            await self.send_message_function(socket_msg.dict())
        return message
            
    def sanitize_agent_spec(self, agent_spec: AgentFlowSpec) -> AgentFlowSpec:
        """
        Sanitizes the agent spec by setting loading defaults

        Args:
            config: The agent configuration to be sanitized.
            agent_type: The type of the agent.

        Returns:
            The sanitized agent configuration.
        """
        if isinstance(agent_spec, dict):
            agent_spec = AgentFlowSpec(**agent_spec)
        
        agent_spec.config.is_termination_msg = agent_spec.config.is_termination_msg or (
            lambda x: "TERMINATE" in x.get("content", "").rstrip()[-20:]
        )

        # sanitize llm_config if present
        if agent_spec.config.llm_config is not False:
            config_list = []
            for llm in agent_spec.config.llm_config.config_list:
                # check if api_key is present either in llm or env variable
                if "api_key" not in llm and "OPENAI_API_KEY" not in os.environ:
                    error_message = f"api_key is not present in llm_config or OPENAI_API_KEY env variable for agent ** {agent_spec.config.name}**. Update your workflow to provide an api_key to use the LLM."
                    raise ValueError(error_message)

                # only add key if value is not None
                sanitized_llm = sanitize_model(llm)
                config_list.append(sanitized_llm)
            agent_spec.config.llm_config.config_list = config_list
        agent_spec.config.code_execution_config = agent_spec.config.code_execution_config or False
        if agent_spec.config.code_execution_config is not False:
            code_execution_config = agent_spec.config.code_execution_config
            code_execution_config["work_dir"] = self.work_dir
            # tbd check if docker is installed
            code_execution_config["use_docker"] = False
            code_execution_config["executor"] = "commandline-local"
            code_execution_config["commandline-local"] = {"work_dir": self.work_dir}
            agent_spec.config.code_execution_config = code_execution_config
        return agent_spec

    def setup_context(self, agent_spec: AgentFlowSpec, session_id: str):
        path_to_data_dir = Path(self.work_dir) / session_id / agent_spec.config.name
        safe_builtins = {
            'True': True,
            'False': False,
            'None': None,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'dict': dict,
            'list': list,
            'tuple': tuple,
            'set': set,
            'frozenset': frozenset,
            'len': len,
            'range': range,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'enumerate': enumerate,
            'isinstance': isinstance,
            'issubclass': issubclass,
            'type': type,
            'id': id,
            'hash': hash,
            'print': print,  # Consider removing if you don't want code to print to stdout.
            'getattr': getattr,
            'setattr': setattr,
            'hasattr': hasattr,
            'delattr': delattr,
            'abs': abs,
            'sum': sum,
            'min': min,
            'max': max,
            'divmod': divmod,
            'round': round,
            'pow': pow,
            'repr': repr,
            'bytes': bytes,
            'bytearray': bytearray,
            'memoryview': memoryview,
            'complex': complex,
            '__import__': __import__,
        }
        # Define the context for exec to limit the accessible variables and functions
        context = {
            'autogen': autogen,
            'path_to_data_dir': path_to_data_dir,
            'agent_spec': agent_spec,
            'session_id': session_id,
            'self': self,
            '__builtins__': safe_builtins
        }
        # Define a placeholder in the context for the agent to be created
        context['agent'] = None
        return context

    def load(self, agent_spec: AgentFlowSpec, session_id: str) -> autogen.Agent:
        """
        Loads an agent based on the provided agent configuration.

        Args:
            agent_config: The configuration of the agent to be loaded.
            agent_type: The type of the agent to be loaded.
            session_id: Session identifier for the current session.

        Returns:
            An instance of the loaded agent.
        """
        agent_spec = self.sanitize_agent_spec(agent_spec)
        context = self.setup_context(agent_spec, session_id)
        # Your init_code should end with assigning the newly created agent to 'agent'
        # For example, init_code could be:
        # """
        # agent = autogen.AssistantAgent(**agent_spec.config.dict())
        # """
        # Ensure your init_code string assigns the instantiated object to 'agent'

        try:
            # Dynamically execute the init_code within the provided context
            exec(agent_spec.init_code, context)
        except Exception as e:
            raise ValueError(f"Failed to initialize agent with init_code. Error: {e}")

        # Retrieve the created agent from the context
        agent: autogen.ConversableAgent = context['agent']

        if agent is None:
            raise ValueError("Initialization code did not correctly create an agent.")
        

        if agent_spec.type == "groupchat" and agent_spec.groupchat_config.send_introductions:
            agent._groupchat.send_introductions = True
        if agent_spec.skills:
            # get skill prompt, also write skills to a file named skills.py
            skills_prompt = get_skills_from_prompt(agent_spec.skills, self.work_dir)
            if agent.system_message:
                agent.update_system_message(agent.system_message + "\n\n" + skills_prompt)
            else:
                agent.update_system_message("You are a helpful assistant.\n\n" + skills_prompt)
        else:
            if not agent.system_message:
                agent.update_system_message("You are a helpful assistant.")
        # Assuming the agent is correctly instantiated, register hooks or perform additional setup
        agent.register_hook(hookable_method="a_process_message_before_send", hook=self.a_process_message_before_send)
        agent.load_state(context['path_to_data_dir'])
        return agent

    async def run(self, message: str, clear_history: bool = False) -> None:
        """
        Initiates a chat between the sender and receiver agents with an initial message
        and an option to clear the history.

        Args:
            message: The initial message to start the chat.
            clear_history: If set to True, clears the chat history before initiating.
        """
        await self.sender.a_initiate_chat(
            self.receiver,
            message=message,
            clear_history=clear_history,
        )
        self.sender.save_state()
        self.receiver.save_state()
        # pass
