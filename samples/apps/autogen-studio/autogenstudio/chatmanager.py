import json
import time
import warnings
from typing import List
from .datamodel import AgentWorkFlowConfig, Message
from .utils import extract_successful_code_blocks, get_default_agent_config, get_modified_files
from .workflowmanager import AutoGenWorkFlowManager
import os
from dotenv import load_dotenv, find_dotenv
from openai import BadRequestError

class AutoGenChatManager:
    def __init__(self) -> None:
        pass

    def chat(self, message: Message, history: List, flow_config: AgentWorkFlowConfig = None, **kwargs) -> None:
        work_dir = kwargs.get("work_dir", None)
        scratch_dir = os.path.join(work_dir, "scratch")
        os.makedirs(scratch_dir, exist_ok=True)
        os.environ['SCRATCH_DIR'] = scratch_dir
        load_dotenv(find_dotenv(usecwd=True))
        # if no flow config is provided, use the default
        if flow_config is None:
            flow_config = get_default_agent_config(scratch_dir)
        flow_config.session_id = message.session_id
        flow = AutoGenWorkFlowManager(config=flow_config, work_dir=scratch_dir, clear_work_dir=False)
        message_text = message.content.strip()

        output = ""
        start_time = time.time()

        metadata = {}
        flow.run(message=f"{message_text}", clear_history=False)
        agent_history = flow.agent_history.copy()
        metadata["messages"] = agent_history

        output_msg = ""
        summary_method = flow_config.summary_method
        if summary_method == "llm":
            prompt = (
            "You have been given the history between the SENDER (user) and RECEIVER (assistant) as well as an internal workflow history within the RECEIVER (the JSON messages between RECEIVER and other agents). "
            "The last message from SENDER to the receiver needs to be answered given your understanding using the workflow history as immediate context. The answer needs to be addressed to the SENDER. "
            "If the last message (not counting single TERMINATE messages) in the internal workflow history already provides a well-structured all-encompassing answer to the SENDER then just return nothing. Disregard TERMINATE messages from your answers, they are there to end the conversation flow only and return to the SENDER.")
            msg_list: list = flow.sender.chat_messages_for_summary(flow.receiver)
            flow_msg_list = build_flow_msg_list(flow.agent_history)
            msg_list.extend(flow_msg_list)
            output = ""
            try:
                output = flow.receiver._reflection_with_llm(prompt, flow_msg_list)
            except BadRequestError as e:
                warnings.warn(f"Cannot extract summary using reflection_with_llm: {e}", UserWarning)
            if output == "" or len(output) <= 10:
                summary_method = "last"
            else:
                successful_code_blocks = extract_successful_code_blocks(agent_history)
                successful_code_blocks = "\n\n".join(successful_code_blocks)
                output_msg = (output + "\n" + successful_code_blocks) if successful_code_blocks else output
        if summary_method == "last":
            successful_code_blocks = extract_successful_code_blocks(agent_history)
            index:int = -1
            last_message = agent_history[index]["message"]["content"] if agent_history else ""
            # if termination and seperated message then the one we care about is the previous message with the answer
            while "TERMINATE" in last_message and len(last_message) <= 10 or last_message == "":
                index = index - 1
                if abs(index) > len(agent_history):
                    break  # Break the loop if index is out of range
                last_message = agent_history[index]["message"]["content"] if agent_history else ""
            successful_code_blocks = "\n\n".join(successful_code_blocks)
            output_msg = (last_message + "\n" + successful_code_blocks) if successful_code_blocks else last_message
        elif summary_method == "none":
            output_msg = ""

        metadata["code"] = ""
        metadata["summary_method"] = summary_method
        end_time = time.time()
        metadata["time"] = end_time - start_time
        modified_files = get_modified_files(start_time, end_time, scratch_dir, dest_dir=work_dir)
        metadata["files"] = modified_files

        print("Modified files: ", len(modified_files))

        output_message = Message(
            user_id=message.user_id,
            root_msg_id=message.root_msg_id,
            role="assistant",
            content=output_msg,
            metadata=json.dumps(metadata),
            session_id=message.session_id,
        )

        return output_message
    
def build_flow_msg_list(flow_history):
    messages = []
    for flow_msg in flow_history:
        messages.append({"role": flow_msg["message"]["role"], "content": json.dumps(flow_msg)})
    return messages
