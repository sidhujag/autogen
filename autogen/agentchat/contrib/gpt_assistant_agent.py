from collections import defaultdict
import json
import time
import logging

from autogen import OpenAIWrapper
from autogen.oai.openai_utils import retrieve_assistants_by_name
from autogen.agentchat.agent import Agent
from autogen.agentchat.assistant_agent import ConversableAgent
from autogen.agentchat.assistant_agent import AssistantAgent
from typing import Dict, Optional, Union, List, Tuple, Any

logger = logging.getLogger(__name__)

class GPTAssistantAgent(ConversableAgent):
    """
    An experimental AutoGen agent class that leverages the OpenAI Assistant API for conversational capabilities.
    This agent is unique in its reliance on the OpenAI Assistant for state management, differing from other agents like ConversableAgent.
    """
    cancellation_requested: bool = False
    cancellation_msg: str = ""
    def __init__(
        self,
        name="GPT Assistant",
        instructions: Optional[str] = None,
        llm_config: Optional[Union[Dict, bool]] = None,
        overwrite_instructions: bool = False,
        overwrite_tools: bool = False,
        **kwargs,
    ):
        """
        Args:
            name (str): name of the agent. It will be used to find the existing assistant by name. Please remember to delete an old assistant with the same name if you intend to create a new assistant with the same name.
            instructions (str): instructions for the OpenAI assistant configuration.
            When instructions is not None, the system message of the agent will be
            set to the provided instructions and used in the assistant run, irrespective
            of the overwrite_instructions flag. But when instructions is None,
            and the assistant does not exist, the system message will be set to
            AssistantAgent.DEFAULT_SYSTEM_MESSAGE. If the assistant exists, the
            system message will be set to the existing assistant instructions.
            llm_config (dict or False): llm inference configuration.
                - assistant_id: ID of the assistant to use. If None, a new assistant will be created.
                - model: Model to use for the assistant (gpt-4-turbo-preview, gpt-3.5-turbo-1106).
                - check_every_ms: check thread run status interval
                - tools: Give Assistants access to OpenAI-hosted tools like Code Interpreter and Knowledge Retrieval,
                        or build your own tools using Function calling. ref https://platform.openai.com/docs/assistants/tools
                - file_ids: files used by retrieval in run
            overwrite_instructions (bool): whether to overwrite the instructions of an existing assistant. This parameter is in effect only when assistant_id is specified in llm_config.
            overwrite_tools (bool): whether to overwrite the tools of an existing assistant. This parameter is in effect only when assistant_id is specified in llm_config.
            kwargs (dict): Additional configuration options for the agent.
                - verbose (bool): If set to True, enables more detailed output from the assistant thread.
                - Other kwargs: Except verbose, others are passed directly to ConversableAgent.
        """
        # Use AutoGen OpenAIWrapper to create a client
        oai_wrapper = OpenAIWrapper(**llm_config)
        if len(oai_wrapper._clients) > 1:
            logger.warning("GPT Assistant only supports one OpenAI client. Using the first client in the list.")
        self._openai_client = oai_wrapper._clients[0]._oai_client
        openai_assistant_id = llm_config.get("assistant_id", None)
        if openai_assistant_id is None:
            # try to find assistant by name first
            candidate_assistants = retrieve_assistants_by_name(self._openai_client, name)
            if len(candidate_assistants) > 0:
                # Filter out candidates with the same name but different instructions, file IDs, and function names.
                candidate_assistants = self.find_matching_assistant(
                    candidate_assistants, instructions, llm_config.get("tools", []), llm_config.get("file_ids", [])
                )

            if len(candidate_assistants) == 0:
                logger.warning("No matching assistant found, creating a new assistant")
                # create a new assistant
                if instructions is None:
                    logger.warning(
                        "No instructions were provided for new assistant. Using default instructions from AssistantAgent.DEFAULT_SYSTEM_MESSAGE."
                    )
                    instructions = AssistantAgent.DEFAULT_SYSTEM_MESSAGE
                self._openai_assistant = self._openai_client.beta.assistants.create(
                    name=name,
                    instructions=instructions,
                    tools=llm_config.get("tools", []),
                    model=llm_config.get("model", "gpt-4-turbo-preview"),
                    file_ids=llm_config.get("file_ids", []),
                )
            else:
                logger.warning(
                    "Matching assistant found, using the first matching assistant: %s",
                    candidate_assistants[0].__dict__,
                )
                self._openai_assistant = candidate_assistants[0]
        else:
            # retrieve an existing assistant
            self._openai_assistant = self._openai_client.beta.assistants.retrieve(openai_assistant_id)
            # if no instructions are provided, set the instructions to the existing instructions
            if instructions is None:
                logger.warning(
                    "No instructions were provided for given assistant. Using existing instructions from assistant API."
                )
                instructions = self.get_assistant_instructions()
            elif overwrite_instructions is True:
                logger.warning(
                    "overwrite_instructions is True. Provided instructions will be used and will modify the assistant in the API"
                )
                self._openai_assistant = self._openai_client.beta.assistants.update(
                    assistant_id=openai_assistant_id,
                    instructions=instructions,
                )
            else:
                logger.warning(
                    "overwrite_instructions is False. Provided instructions will be used without permanently modifying the assistant in the API."
                )

            # Check if tools are specified in llm_config
            specified_tools = llm_config.get("tools", None)

            if specified_tools is None:
                # Check if the current assistant has tools defined
                if self._openai_assistant.tools:
                    logger.warning(
                        "No tools were provided for given assistant. Using existing tools from assistant API."
                    )
                else:
                    logger.info(
                        "No tools were provided for the assistant, and the assistant currently has no tools set."
                    )
            elif overwrite_tools is True:
                # Tools are specified and overwrite_tools is True; update the assistant's tools
                logger.warning(
                    "overwrite_tools is True. Provided tools will be used and will modify the assistant in the API"
                )
                self._openai_assistant = self._openai_client.beta.assistants.update(
                    assistant_id=openai_assistant_id,
                    tools=llm_config.get("tools", []),
                )
            else:
                # Tools are specified but overwrite_tools is False; do not update the assistant's tools
                logger.warning("overwrite_tools is False. Using existing tools from assistant API.")

        self._verbose = kwargs.pop("verbose", False)
        super().__init__(
            name=name, system_message=instructions, llm_config=llm_config, **kwargs
        )
        # lazly create thread

        # lazily create threads
        self._openai_threads = {}
        self._unread_index = defaultdict(int)
        self.register_reply([Agent, None], GPTAssistantAgent._invoke_assistant, position=1)

    @staticmethod
    def check_for_cancellation():
        """
        Checks for cancellation used during _get_run_response
        """
        return GPTAssistantAgent.cancellation_requested

    @staticmethod
    def cancel_run(cancel_msg: str):
        GPTAssistantAgent.cancellation_requested = True
        GPTAssistantAgent.cancellation_msg = cancel_msg

    async def execute_run(self, assistant_thread, max_retries=5):
        retries = 0
        run = None
        response = None
        while retries < max_retries:
            try:
                # Attempt to create a new run to get responses from the assistant
                run = self._openai_client.beta.threads.runs.create(
                    thread_id=assistant_thread.id,
                    assistant_id=self._openai_assistant.id,
                    instructions=self.system_message,
                )
                # If the run was created successfully, get the response
                response, run = await self._get_run_response(assistant_thread, run)
                # Check if the run failed due to a server error
                if run and run.status == "failed" and run.last_error:
                    if (run.last_error.code == 'server_error' and 
                        run.last_error.message == 'Sorry, something went wrong.'):
                        retries += 1
                        print(f"Attempt {retries} failed with server error: {run.last_error.message}")
                        if retries < max_retries:
                            print("Retrying...")
                            continue
                        else:
                            print("Max retries reached. Giving up.")
                            break
                    else:
                        # Handle other types of errors that might be present
                        print(f"Run failed with a different error: {run.last_error.message}")
                        break
                break  # Exit loop if successful
            except KeyboardInterrupt:
                self._cancel_run(run.id, assistant_thread.id)
                GPTAssistantAgent.cancellation_requested = False
                GPTAssistantAgent.cancellation_msg = ""
                raise
            except Exception as e:
                # If run is None or there's no last_error, it's an unexpected situation
                print(f"An unexpected error occurred: {e}")
                break

        GPTAssistantAgent.cancellation_requested = False
        GPTAssistantAgent.cancellation_msg = ""
        return response
    
    async def _invoke_assistant(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """
        Invokes the OpenAI assistant to generate a reply based on the given messages.

        Args:
            messages: A list of messages in the conversation history with the sender.
            sender: The agent instance that sent the message.
            config: Optional configuration for message processing.

        Returns:
            A tuple containing a boolean indicating success and the assistant's reply.
        """
        from ..groupchat import GroupChatManager
        from ..service import GroupService
        if messages is None:
            messages = self._oai_messages[sender]
        unread_index = self._unread_index[sender] or 0
        pending_messages = messages[unread_index:]
        # Check and initiate a new thread if necessary
        if self._openai_threads.get(sender, None) is None:
            msgs = []
            if isinstance(sender, GroupChatManager):
                group_response = json.loads(await GroupService.get_group_info(sender.name, True))
                group_intro = f'To start this thread of conversation amongst multiple agents, I will give you group information and agents inside it, please note new agents may come, some may leave and you are to track them as you conversate within a group of agents. Note the instructions for each assistant in the thread and instructions every time you are asked to respond which will be for the assistant thats responding to the conversation. Assistant messages come from API responses from the agent in the previous message. For those that have termination access, terminate if you see the discussion and going in circles, to save costs. Do not terminate if a path does not work out right away, exhaust all of your possibilities to try different things to try to solve the problem. If the conversation shows there is a satisfactory answer already, terminate. If you have nothing to add either terminate or say you have nothing to add. Ensure the responses reflect the groups message history. Group Info: {group_response["response"]}'
                msgs.append({
                    "role": "user",
                    "content": group_intro,
                })
            self._openai_threads[sender] = self._openai_client.beta.threads.create(
                messages=msgs,
            )
        assistant_thread = self._openai_threads[sender]
        # Process each unread message
        for message in pending_messages:
            self._openai_client.beta.threads.messages.create(
                thread_id=assistant_thread.id,
                content=message["content"],
                role="user",
            )
        #self.pretty_print_thread(assistant_thread)
        
        response = await self.execute_run(assistant_thread)
        self._unread_index[sender] = len(self._oai_messages[sender]) + 1
        if response and "content" in response and response["content"]:
            return True, response
        else:
            return False, "No response from the assistant."

    def _process_messages(self, assistant_thread, run):
        """
        Processes and provides a response based on the run status.
        Args:
            assistant_thread: The thread object for the assistant.
            run: The run object initiated with the OpenAI assistant.
        """
        if run.status == "failed":
            logger.error(f'Run: {run.id} Thread: {assistant_thread.id}: failed...')
            if run.last_error:
                response = {
                    "role": "assistant",
                    "content": str(run.last_error),
                }
            else:
                response = {
                    "role": "assistant",
                    "content": 'Failed',
                }
            return response, run
        elif run.status == "expired":
            logger.warn(f'Run: {run.id} Thread: {assistant_thread.id}: expired...')
            response = {
                "role": "assistant",
                "content": 'Expired',
            }
            return new_messages, run
        elif run.status == "cancelled":
            logger.warn(f'Run: {run.id} Thread: {assistant_thread.id}: cancelled...')
            response = {
                "role": "assistant",
                "content": 'Run Cancelled',
            }
            if GPTAssistantAgent.cancellation_msg != "":
                response["content"] = GPTAssistantAgent.cancellation_msg
            return response, run
        elif run.status == "completed":
            logger.info(f'Run: {run.id} Thread: {assistant_thread.id}: completed...')
            response_messages = self._openai_client.beta.threads.messages.list(assistant_thread.id, order="asc")
            new_messages = []
            for msg in response_messages:
                if msg.run_id == run.id:
                    for content in msg.content:
                        if content.type == "text":
                            new_messages.append(
                                {"role": msg.role, "content": self._format_assistant_message(content.text)}
                            )
                        elif content.type == "image_file":
                            new_messages.append(
                                {
                                    "role": msg.role,
                                    "content": f"Received file id={content.image_file.file_id}",
                                }
                            )
            response = {
                "role": new_messages[-1]["role"],
                "content": "",
            }
            for message in new_messages:
                # just logging or do something with the intermediate messages?
                # if current response is not empty and there is more, append new lines
                if len(response["content"]) > 0:
                    response["content"] += "\n\n"
                response["content"] += message["content"]
            return response, run

    async def _get_run_response(self, assistant_thread, run):
        """
        Waits for and processes the response of a run from the OpenAI assistant.
        Args:
            assistant_thread: The thread object for the assistant.
            run: The run object initiated with the OpenAI assistant.
        """
        from autogen.agentchat.service import GetFunctionModel, FunctionsService
        while True:
            run = self._openai_client.beta.threads.runs.retrieve(run.id, thread_id=assistant_thread.id)
            if run.status == "in_progress" or run.status == "queued":
                time.sleep(self.llm_config.get("check_every_ms", 1000) / 1000)
            elif run.status == "completed" or run.status == "cancelled" or run.status == "expired" or run.status == "failed":
                return self._process_messages(assistant_thread, run)
            elif run.status == "cancelling":
                logger.warn(f'Run: {run.id} Thread: {assistant_thread.id}: cancelling...')
            elif run.status == "requires_action":
                logger.info(f'Run: {run.id} Thread: {assistant_thread.id}: required action...')
                actions = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    function = tool_call.function
                    function_dict = function.dict()
                    # if function not found in function map then try to find it from registry and add it before executing
                    if not self.can_execute_function(function_dict["name"]):
                        function = await FunctionsService.get_functions([GetFunctionModel(name=function_dict["name"])])
                        if function:
                            response = FunctionsService.define_function_internal(self, function[0])
                            logger.info(f"Tool definition on demand ({function_dict['name']}), response: {response}")
                    is_exec_success, tool_response = await self.a_execute_function(function_dict)
                    tool_response["metadata"] = {
                        "tool_call_id": tool_call.id,
                        "run_id": run.id,
                        "thread_id": assistant_thread.id,
                    }

                    logger.info(
                        "Intermediate executing(%s, Success: %s) : %s",
                        tool_response["name"],
                        is_exec_success,
                        tool_response["content"],
                    )
                    actions.append(tool_response)

                submit_tool_outputs = {
                    "tool_outputs": [
                        {"output": action["content"], "tool_call_id": action["metadata"]["tool_call_id"]}
                        for action in actions
                    ],
                    "run_id": run.id,
                    "thread_id": assistant_thread.id,
                }
                if GPTAssistantAgent.check_for_cancellation():
                    self._cancel_run(run.id, assistant_thread.id)
                else:
                    run = self._openai_client.beta.threads.runs.submit_tool_outputs(**submit_tool_outputs)
            else:
                run_info = json.dumps(run.dict(), indent=2)
                raise ValueError(f"Unexpected run status: {run.status}. Full run info:\n\n{run_info})")


    def _cancel_run(self, run_id: str, thread_id: str):
        """
        Cancels a run.

        Args:
            run_id: The ID of the run.
            thread_id: The ID of the thread associated with the run.
        """
        try:
            self._openai_client.beta.threads.runs.cancel(run_id=run_id, thread_id=thread_id)
            logger.info(f'Run: {run_id} Thread: {thread_id}: successfully sent cancellation signal.')
        except Exception as e:
            logger.error(f'Run: {run_id} Thread: {thread_id}: failed to send cancellation signal: {e}')


    def _format_assistant_message(self, message_content):
        """
        Formats the assistant's message to include annotations and citations.
        """
        annotations = message_content.annotations
        citations = []

        # Iterate over the annotations and add footnotes
        for index, annotation in enumerate(annotations):
            # Replace the text with a footnote
            message_content.value = message_content.value.replace(annotation.text, f" [{index}]")

            # Gather citations based on annotation attributes
            if file_citation := getattr(annotation, "file_citation", None):
                try:
                    cited_file = self._openai_client.files.retrieve(file_citation.file_id)
                    citations.append(f"[{index}] {cited_file.filename}: {file_citation.quote}")
                except Exception as e:
                    logger.error(f"Error retrieving file citation: {e}")
            elif file_path := getattr(annotation, "file_path", None):
                try:
                    cited_file = self._openai_client.files.retrieve(file_path.file_id)
                    citations.append(f"[{index}] Click <here> to download {cited_file.filename}")
                except Exception as e:
                    logger.error(f"Error retrieving file citation: {e}")
                # Note: File download functionality not implemented above for brevity

        # Add footnotes to the end of the message before displaying to user
        message_content.value += "\n" + "\n".join(citations)
        return message_content.value

    def reset(self):
        """
        Resets the agent, clearing any existing conversation thread and unread message indices.
        """
        super().reset()
        for thread in self._openai_threads.values():
            # Delete the existing thread to start fresh in the next conversation
            self._openai_client.beta.threads.delete(thread.id)
        self._openai_threads = {}
        # Clear the record of unread messages
        self._unread_index.clear()

    def clear_history(self, agent: Optional[Agent] = None):
        """Clear the chat history of the agent.

        Args:
            agent: the agent with whom the chat history to clear. If None, clear the chat history with all agents.
        """
        super().clear_history(agent)
        if self._openai_threads.get(agent, None) is not None:
            # Delete the existing thread to start fresh in the next conversation
            thread = self._openai_threads[agent]
            logger.info("Clearing thread %s", thread.id)
            self._openai_client.beta.threads.delete(thread.id)
            self._openai_threads.pop(agent)
            self._unread_index[agent] = 0

    def pretty_print_thread(self, thread):
        """Pretty print the thread."""
        if thread is None:
            print("No thread to print")
            return
        messages = self._openai_client.beta.threads.messages.list(
            thread_id=thread.id,
        )
        print("~~~~~~~THREAD CONTENTS~~~~~~~")
        for message in messages:
            content_types = [content.type for content in message.content]
            print(f"[{message.created_at}]", message.role, ": [", ", ".join(content_types), "]")
            for content in message.content:
                content_type = content.type
                if content_type == "text":
                    print(content.type, ": ", content.text.value)
                elif content_type == "image_file":
                    print(content.type, ": ", content.image_file.file_id)
                else:
                    print(content.type, ": ", content)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    @property
    def oai_threads(self) -> Dict[Agent, Any]:
        """Return the threads of the agent."""
        return self._openai_threads

    @property
    def assistant_id(self):
        """Return the assistant id"""
        return self._openai_assistant.id

    @property
    def openai_client(self):
        return self._openai_client

    def get_assistant_instructions(self):
        """Return the assistant instructions from OAI assistant API"""
        return self._openai_assistant.instructions

    def delete_assistant(self):
        """Delete the assistant from OAI assistant API"""
        logger.warning("Permanently deleting assistant...")
        self._openai_client.beta.assistants.delete(self.assistant_id)

    def find_matching_assistant(self, candidate_assistants, instructions, tools, file_ids):
        """
        Find the matching assistant from a list of candidate assistants.
        Filter out candidates with the same name but different instructions, file IDs, and function names.
        TODO: implement accurate match based on assistant metadata fields.
        """
        matching_assistants = []

        # Preprocess the required tools for faster comparison
        required_tool_types = set(tool.get("type") for tool in tools)
        required_function_names = set(
            tool.get("function", {}).get("name")
            for tool in tools
            if tool.get("type") not in ["code_interpreter", "retrieval"]
        )
        required_file_ids = set(file_ids)  # Convert file_ids to a set for unordered comparison

        for assistant in candidate_assistants:
            # Check if instructions are similar
            if instructions and instructions != getattr(assistant, "instructions", None):
                logger.warning(
                    "instructions not match, skip assistant(%s): %s",
                    assistant.id,
                    getattr(assistant, "instructions", None),
                )
                continue

            # Preprocess the assistant's tools
            assistant_tool_types = set(tool.type for tool in assistant.tools)
            assistant_function_names = set(tool.function.name for tool in assistant.tools if hasattr(tool, "function"))
            assistant_file_ids = set(getattr(assistant, "file_ids", []))  # Convert to set for comparison

            # Check if the tool types, function names, and file IDs match
            if required_tool_types != assistant_tool_types or required_function_names != assistant_function_names:
                logger.warning(
                    "tools not match, skip assistant(%s): tools %s, functions %s",
                    assistant.id,
                    assistant_tool_types,
                    assistant_function_names,
                )
                continue
            if required_file_ids != assistant_file_ids:
                logger.warning("file_ids not match, skip assistant(%s): %s", assistant.id, assistant_file_ids)
                continue

            # Append assistant to matching list if all conditions are met
            matching_assistants.append(assistant)

        return matching_assistants
