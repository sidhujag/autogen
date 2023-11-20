from collections import defaultdict
import json
import time
import logging

from autogen import OpenAIWrapper
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

    def __init__(
        self,
        name="GPT Assistant",
        instructions: Optional[str] = None,
        llm_config: Optional[Union[Dict, bool]] = None,
        overwrite_instructions: bool = False,
        **kwargs,
    ):
        """
        Args:
            name (str): name of the agent.
            instructions (str): instructions for the OpenAI assistant configuration.
            When instructions is not None, the system message of the agent will be
            set to the provided instructions and used in the assistant run, irrespective
            of the overwrite_instructions flag. But when instructions is None,
            and the assistant does not exist, the system message will be set to
            AssistantAgent.DEFAULT_SYSTEM_MESSAGE. If the assistant exists, the
            system message will be set to the existing assistant instructions.
            llm_config (dict or False): llm inference configuration.
                - assistant_id: ID of the assistant to use. If None, a new assistant will be created.
                - model: Model to use for the assistant (gpt-4-1106-preview, gpt-3.5-turbo-1106).
                - check_every_ms: check thread run status interval
                - tools: Give Assistants access to OpenAI-hosted tools like Code Interpreter and Knowledge Retrieval,
                        or build your own tools using Function calling. ref https://platform.openai.com/docs/assistants/tools
                - file_ids: files used by retrieval in run
            overwrite_instructions (bool): whether to overwrite the instructions of an existing assistant.
        """
        # Use AutoGen OpenAIWrapper to create a client
        oai_wrapper = OpenAIWrapper(**llm_config)
        if len(oai_wrapper._clients) > 1:
            logger.warning("GPT Assistant only supports one OpenAI client. Using the first client in the list.")
        self._openai_client = oai_wrapper._clients[0]
        openai_assistant_id = llm_config.get("assistant_id", None)
        if openai_assistant_id is None:
            logger.warning("assistant_id was None, creating a new assistant")
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
                model=llm_config.get("model", "gpt-4-1106-preview"),
                file_ids=llm_config.get("file_ids", []),
            )
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
        super().__init__(
            name=name,
            system_message=instructions,
            llm_config=llm_config,
            **kwargs
        )
        self.cancellation_requested = False
        # lazly create thread
        self._openai_threads = {}
        self._unread_index = defaultdict(int)
        self.register_reply([Agent, None], GPTAssistantAgent._invoke_assistant, position=1)

    def check_for_cancellation(self):
        """
        Checks for cancellation used during _get_run_response
        """
        return self.cancellation_requested

    def _invoke_assistant(
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
        if messages is None:
            messages = self._oai_messages[sender]
        unread_index = self._unread_index[sender] or 0
        pending_messages = messages[unread_index:]

        # Check and initiate a new thread if necessary
        if self._openai_threads.get(sender, None) is None:
            self._openai_threads[sender] = self._openai_client.beta.threads.create(
                messages=[],
            )
        assistant_thread = self._openai_threads[sender]
        # Process each unread message
        for message in pending_messages:
            self._openai_client.beta.threads.messages.create(
                thread_id=assistant_thread.id,
                content=message["content"],
                role="user",
            )
        # Create a new run to get responses from the assistant
        run = self._openai_client.beta.threads.runs.create(
            thread_id=assistant_thread.id,
            assistant_id=self._openai_assistant.id,
            # pass the latest system message as instructions
            instructions=self.system_message,
        )
        self.cancellation_requested = False
        response = self._get_run_response(assistant_thread, run)
        self._unread_index[sender] = len(self._oai_messages[sender]) + 1
        if response["content"]:
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
            return response
        elif run.status == "expired":
            logger.warn(f'Run: {run.id} Thread: {assistant_thread.id}: expired...')
            response = {
                "role": "assistant",
                "content": 'Expired',
            }
            return new_messages
        elif run.status == "cancelled":
            logger.warn(f'Run: {run.id} Thread: {assistant_thread.id}: cancelled...')
            response = {
                "role": "assistant",
                "content": 'Cancelled',
            }
            return response
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
                                    "content": f"Recieved file id={content.image_file.file_id}",
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
            return response

    def _get_run_response(self, assistant_thread, run):
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
                run = self._openai_client.beta.threads.runs.retrieve(run.id, thread_id=assistant_thread.id)
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
                        function = FunctionsService.get_functions([GetFunctionModel(auth=self.auth, name=function_dict["name"])])
                        if function:
                            response = FunctionsService.define_function_internal(self, function[0])
                            logger.info(f"Tool definition on demand ({function_dict['name']}), response: {response}")
                    is_exec_success, tool_response = self.execute_function(function_dict)
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

                run = self._openai_client.beta.threads.runs.submit_tool_outputs(**submit_tool_outputs)
                if self.check_for_cancellation():
                    self._cancel_run()
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
