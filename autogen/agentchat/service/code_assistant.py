import json
import copy
import logging
from typing import Dict, List, Optional, Union, Callable, Literal, Tuple
from autogen import Agent, ConversableAgent, AssistantAgent, UserProxyAgent, OpenAIWrapper
from datetime import datetime
from pathlib import Path
from functools import partial

logger = logging.getLogger(__name__)


class CodeAssistantAgent(ConversableAgent):
    """(In preview) An agent that acts as a code assistant to work on code through natural language instructions."""

    DEFAULT_PROMPT = (
        "You are a helpful AI code assistant (via the provided functions). In fact, YOU ARE THE ONLY MEMBER OF YOUR PARTY WITH ACCESS TO CODE ASSISTANT TOOLS, so please help out where you can by performing code assistant related activities and reporting what you find. Today's date is "
        + datetime.now().date().isoformat()
    )

    DEFAULT_DESCRIPTION = "A helpful code assistant. Ask them to perform create software or documents for software design."

    def __init__(
        self,
        name,
        system_message: Optional[Union[str, List]] = DEFAULT_PROMPT,
        description: Optional[str] = DEFAULT_DESCRIPTION,
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[str] = "TERMINATE",
        function_map: Optional[Dict[str, Callable]] = None,
        code_execution_config: Optional[Union[Dict, Literal[False]]] = None,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        default_auto_reply: Optional[Union[str, Dict, None]] = "",
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            description=description,
            is_termination_msg=is_termination_msg,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            function_map=function_map,
            code_execution_config=code_execution_config,
            llm_config=llm_config,
            default_auto_reply=default_auto_reply,
        )


        # Create a copy of the llm_config for the inner monologue agents to use, and set them up with function calling
        if llm_config is None:  # Nothing to copy
            inner_llm_config = None
        elif llm_config is False:  # LLMs disabled
            inner_llm_config = False
        else:
            inner_llm_config = copy.deepcopy(llm_config)
            inner_llm_config["functions"] = [
                {
                    "name": "command_add",
                    "description": "Add matching files to the chat session using glob patterns to your local branch. You can specify a file name without pattern as well. Will touch a new file if the file doesn't exist on disk (not using pattern). If you are considering a `git add` operation use this instead.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_glob": {
                                "type": "string",
                                "description": "File(s) to add to code assistant context.",
                            }
                        },
                    },
                    "required": ["file_glob"],
                },
                {
                    "name": "command_drop",
                    "description": "Remove matching files from the chat session using glob patterns from your local branch. You can specify file name without pattern as well.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_glob": {
                                "type": "string",
                                "description": "File(s) to remove from code assistant context.",
                            }
                        },
                    },
                    "required": ["file_glob"],
                },
                {
                    "name": "command_clear",
                    "description": "Clear the coding assistant chat history of your local branch.",
                    "parameters": {"type": "object", "properties": {}},
                    "required": [],
                },
                {
                    "name": "command_ls",
                    "description": "List all known files and indicate which are included in the code assistant session.",
                    "parameters": {"type": "object", "properties": {}},
                    "required": [],
                },
                {
                    "name": "command_tokens",
                    "description": "Report on the number of tokens used by the current chat context dealing with your local branch.",
                    "parameters": {"type": "object", "properties": {}},
                    "required": [],
                },
                {
                    "name": "command_undo",
                    "description": "Undo the last git commit your local branch if it was done by code assistant.",
                    "parameters": {"type": "object", "properties": {}},
                    "required": [],
                },
                {
                    "name": "command_diff",
                    "description": "Display the diff of the last code assistant commit in your local branch.",
                    "parameters": {"type": "object", "properties": {}},
                    "required": [],
                },
                {
                    "name": "command_git_command",
                    "description": "Run a specified git command against the local branch using the GitPython library with `repo.git.execute(command_git_command.split())`. Examples: 'checkout feature-branch' to switch branches, 'add .' to add all files to staging, 'commit -m \"Your commit message\"' to commit changes, 'push' to push to remote, 'push -u origin feature-branch' to push to a new remote branch, 'pull origin main' to update from main, 'merge another-branch' to merge branches, 'branch' to list branches, 'status' for current status, 'log' to view commit history.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Git command to execute against the repository.",
                            }
                        },
                    },
                    "required": ["command"],
                },
                {
                    "name": "command_show_repo_map",
                    "description": "Print the local repository map. Repository map is how the coding assistant efficiently maps the logical connection between files/objects/classes in the repository.",
                    "parameters": {"type": "object", "properties": {}},
                    "required": [],
                },
                {
                    "name": "command_show_file",
                    "description": "Show contents of a file in the repository. Give the file name with any relative path if necessary.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "file name to show.",
                            }
                        },
                    },
                    "required": ["file_path"],
                },
                {
                    "name": "command_message",
                    "description": "Process a single message for code assistant. This is your entrypoint for natural language coding assistance usually. Work is done in your local branch. You should refer to relevant files (added to context) for any contextual awareness required for tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "msg": {
                                "type": "string",
                                "description": "Task or message to send to coding assistant for proecessing.",
                            }
                        },
                    },
                    "required": ["msg"],
                },
                {
                    "name": "show_help",
                    "description": "Show help, commands you can call the coding assistant with.",
                    "parameters": {"type": "object", "properties": {}},
                    "required": [],
                },
            ]


        # Set up the inner monologue
        self._assistant = AssistantAgent(
            self.name + "_inner_assistant",
            system_message=system_message,
            llm_config=inner_llm_config,
            is_termination_msg=lambda m: False,
        )

        self._user_proxy = UserProxyAgent(
            self.name + "_inner_user_proxy",
            human_input_mode="NEVER",
            code_execution_config=False,
            default_auto_reply="",
            is_termination_msg=lambda m: False,
        )
        # set at runtime
        self.current_group = None
        self.coder = None
        self.code_repository = None
        
        async def async_wrapper(func, *args, **kwargs):
            # Convert keyword arguments to a list of their values
            combined_args = list(kwargs.values())
            return await func(combined_args)

        self._user_proxy.register_function(
            function_map={
                "command_message": partial(async_wrapper, self._command_message),
                "command_show_repo_map": partial(async_wrapper, self._command_show_repo_map),
                "command_add": partial(async_wrapper, self._command_add),
                "command_drop": partial(async_wrapper, self._command_drop),
                "command_clear": partial(async_wrapper, self._command_clear),
                "command_ls": partial(async_wrapper, self._command_ls),
                "command_show_file": partial(async_wrapper, self._command_show_file),
                "command_tokens": partial(async_wrapper, self._command_tokens),
                "command_undo": partial(async_wrapper, self._command_undo),
                "command_diff": partial(async_wrapper, self._command_diff),
                "command_git_command": partial(async_wrapper, self._command_git_command),
                "show_help": partial(async_wrapper, self._show_help),
            }
        )

        self._reply_func_list = []
        self.register_reply([Agent, None], CodeAssistantAgent.a_generate_code_assistant_reply, ignore_async_in_sync_chat=True)
        self.register_reply([Agent, None], ConversableAgent.generate_code_execution_reply)
        self.register_reply([Agent, None], ConversableAgent.a_generate_tool_calls_reply, ignore_async_in_sync_chat=True)
        self.register_reply([Agent, None], ConversableAgent.a_generate_function_call_reply, ignore_async_in_sync_chat=True)
        self.register_reply([Agent, None], ConversableAgent.check_termination_and_human_reply)

        self._user_proxy._reply_func_list = []
        self._user_proxy.register_reply([Agent, None], ConversableAgent.a_generate_oai_reply, ignore_async_in_sync_chat=True)
        self._user_proxy.register_reply([Agent, None], ConversableAgent.generate_code_execution_reply)
        self._user_proxy.register_reply([Agent, None], ConversableAgent.a_generate_tool_calls_reply, ignore_async_in_sync_chat=True)
        self._user_proxy.register_reply(
            [Agent, None], ConversableAgent.a_generate_function_call_reply, ignore_async_in_sync_chat=True
        )
        self._user_proxy.register_reply(
            [Agent, None], ConversableAgent.a_check_termination_and_human_reply, ignore_async_in_sync_chat=True
        )

    async def _command_add(self, args):
        from . import UpsertCodingAssistantModel, CodingAssistantService
        file_glob = args[0]
        if not file_glob or not isinstance(file_glob, str):
            return json.dumps({"error": f"Expected file glob as a string, got {type(file_glob)}"})

        logging.info(f"send_command_to_coding_assistant command_add: {file_glob}")
        self.coder.io.console.begin_capture()
        self.coder.commands.cmd_add(file_glob)
        coding_assistants, err = await CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
            name=self.name,
            files=list(self.coder.abs_fnames)
        )])
        if err is not None:
            logging.error(f"command_add failed: {err}")
            return err
        str_output = self.coder.io.console.end_capture()
        return json.dumps({"success": f"command_add: {str_output}"})
        
    async def _command_drop(self, args):
        from . import UpsertCodingAssistantModel, CodingAssistantService
        file_glob = args[0]
        if not file_glob or not isinstance(file_glob, str):
            return json.dumps({"error": f"Expected file glob as a string, got {type(file_glob)}"})

        logging.info(f"send_command_to_coding_assistant command_drop: {file_glob}")
        self.coder.io.console.begin_capture()
        self.coder.commands.cmd_drop(file_glob)
        coding_assistants, err = await CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
            name=self.name,
            files=list(self.coder.abs_fnames)
        )])
        if err is not None:
            logging.error(f"command_drop failed: {err}")
            return err
        str_output = self.coder.io.console.end_capture()
        return json.dumps({"success": f"command_drop: {str_output}"})
    
    async def _command_clear(self, args):
        logging.info("send_command_to_coding_assistant cmd_clear")
        self.coder.io.console.begin_capture()
        self.coder.commands.cmd_clear(None)
        str_output = self.coder.io.console.end_capture()
        return json.dumps({"success": f"command_clear: {str_output}"})
    
    async def _command_ls(self, args):
        logging.info("send_command_to_coding_assistant command_ls")
        self.coder.io.console.begin_capture()
        self.coder.commands.cmd_ls(None)
        str_output = self.coder.io.console.end_capture()
        return json.dumps({"success": f"command_ls: {str_output}"})
    
    async def _command_tokens(self, args):
        logging.info("send_command_to_coding_assistant command_tokens")
        self.coder.io.console.begin_capture()
        self.coder.commands.cmd_tokens(None)
        str_output = self.coder.io.console.end_capture()
        return json.dumps({"success": f"command_tokens: {str_output}"})
    
    async def _command_undo(self, args):
        logging.info("send_command_to_coding_assistant command_undo")
        self.coder.io.console.begin_capture()
        self.coder.commands.cmd_undo(None)
        str_output = self.coder.io.console.end_capture()
        return json.dumps({"success": f"command_undo: {str_output}"})
    
    async def _command_diff(self, args):
        logging.info("send_command_to_coding_assistant command_diff")
        self.coder.io.console.begin_capture()
        self.coder.commands.cmd_diff(None)
        str_output = self.coder.io.console.end_capture()
        return json.dumps({"success": f"command_diff: {str_output}"})
    
    async def _command_git_command(self, args):
        from . import BackendService, CodeExecInput
        command = args[0]
        if not command or not isinstance(command, str):
            return json.dumps({"error": f"Expected command as a string, got {type(command)}"})

        logging.info(f"send_command_to_coding_assistant command_git_command {command}")
        response, err = await BackendService.execute_git_command(CodeExecInput(
            workspace=self.code_repository.workspace,
            command_git_command=command,
        ))
        if err is not None:
            logging.error(f"command_git_command failed: {err}")
            return err
        return response
    
    async def _command_show_repo_map(self, args):
        logging.info("send_command_to_coding_assistant command_show_repo_map")
        self.coder.io.console.begin_capture()
        repo_map = self.coder.get_repo_map()
        if repo_map:
            self.coder.io.tool_output(repo_map)
        str_output = self.coder.io.console.end_capture()
        return json.dumps({"success": f"command_show_repo_map: {str_output}"})
    
    async def _command_show_file(self, args):
        from . import CodingAssistantService
        file_path = args[0]
        if not file_path or not isinstance(file_path, str):
            return json.dumps({"error":f"Expected file path as a string, got {type(file_path)}"})

        logging.info(f"send_command_to_coding_assistant command_show_file {file_path}")
        text, err = CodingAssistantService.show_file(file_path, Path(self.code_repository.workspace))
        if err is not None:
            logging.error(f"command_show_file failed: {err}")
            return err
        return text


    async def _command_message(self, args):
        from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
        from . import CodingAssistantService, GroupService

        msg = args[0]
        if not msg or not isinstance(msg, str):
            return json.dumps({"error": f"Expected message as a string, got {type(msg)}"})

        logging.info(f"send_command_to_coding_assistant command_message {msg}")

        # cancel any assistant run so we can get group chat to run the code assistant
        GPTAssistantAgent.cancel_run("Sent command to coding assistant, getting response...")

        # Wrapper function for starting the code assistance task
        def setup_code_assistance_event_task():
            async def start_task():
                return await GroupService.start_code_assistance_task(
                    CodingAssistantService.run_code_assistant,
                    GroupService.process_code_assistance_results,
                    self.coder,
                    self.code_repository,
                    msg
                )
            return start_task

        self.current_group.code_assistance_event_task = setup_code_assistance_event_task()
        self.current_group.code_assistance_event_task_msg = f"Code assistant command: {msg}"
        str_output = "Ran coding assistant. Please wait for results."
        return json.dumps({"success": f"command_message: {str_output}"})

    async def _show_help(self, args):
        available_commands = {
            "available commands, use natural language to invoke them": {
                "command_message": {
                    "type": "string",
                    "description": "Process a single message for code assistant. This is your entrypoint for natural language coding assistance usually. Work is done in your local branch. You should refer to relevant files (added to context) for any contextual awareness required for tasks."
                },
                "command_show_repo_map": {
                    "type": "boolean",
                    "description": "Print the local repository map. Repository map is how the coding assistant efficiently maps the logical connection between files/objects/classes in the repository."
                },
                "command_add": {
                    "type": "string",
                    "description": "Add matching files to the chat session using glob patterns to your local branch. You can specify a file name without pattern as well. Will touch a new file if the file doesn't exist on disk (not using pattern). If you are considering a `git add` operation use this instead."
                },
                "command_drop": {
                    "type": "string",
                    "description": "Remove matching files from the chat session using glob patterns from your local branch. You can specify file name without pattern as well."
                },
                "command_clear": {
                    "type": "boolean",
                    "description": "Clear the coding assistant chat history of your local branch."
                },
                "command_ls": {
                    "type": "boolean",
                    "description": "List all known files and indicate which are included in the code assistant session."
                },
                "command_show_file": {
                    "type": "string",
                    "description": "Show contents of a file in the repository. Give the file name with any relative path if necessary."
                },
                "command_tokens": {
                    "type": "boolean",
                    "description": "Report on the number of tokens used by the current chat context dealing with your local branch."
                },
                "command_undo": {
                    "type": "boolean",
                    "description": "Undo the last git commit your local branch if it was done by code assistant."
                },
                "command_diff": {
                    "type": "boolean",
                    "description": "Display the diff of the last code assistant commit in your local branch."
                },
                "command_git_command": {
                    "type": "string",
                    "description": "Run a specified git command against the local branch using the GitPython library with `repo.git.execute(command_git_command.split())`. Examples: 'checkout feature-branch' to switch branches, 'add .' to add all files to staging, 'commit -m \"Your commit message\"' to commit changes, 'push' to push to remote, 'push -u origin feature-branch' to push to a new remote branch, 'pull origin main' to update from main, 'merge another-branch' to merge branches, 'branch' to list branches, 'status' for current status, 'log' to view commit history."
                }
            }
        }
        return available_commands 
    async def a_generate_code_assistant_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[OpenAIWrapper] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """Generate a reply using autogen.oai."""
        if messages is None:
            messages = self._oai_messages[sender]

        self._user_proxy.reset()
        self._assistant.reset()

        # Clone the messages to give context
        self._assistant.chat_messages[self._user_proxy] = list()
        history = messages[0 : len(messages) - 1]
        for message in history:
            self._assistant.chat_messages[self._user_proxy].append(message)

        # Remind the agent where it is
        await self._user_proxy.a_send(
            f"You are code assistant '{self.coder.name}' working on repository '{self.coder.repository_name}'.",
            self._assistant,
            request_reply=False,
            silent=True,
        )

        await self._user_proxy.a_send(messages[-1]["content"], self._assistant, request_reply=True, silent=True)
        agent_reply = self._user_proxy.chat_messages[self._assistant][-1]
        #print("Agent Reply: " + str(agent_reply))
        proxy_reply = await self._user_proxy.a_generate_reply(
            messages=self._user_proxy.chat_messages[self._assistant], sender=self._assistant
        )
        #print("Proxy Reply: " + str(proxy_reply))

        if proxy_reply == "":  # Was the default reply
            return True, None if agent_reply is None else agent_reply["content"]
        else:
            return True, None if proxy_reply is None else proxy_reply["content"]
