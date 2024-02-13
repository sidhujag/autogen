import json
import time
from typing import List
from .datamodel import AgentWorkFlowConfig, Message
from .utils import extract_successful_code_blocks, get_default_agent_config, get_modified_files
from .workflowmanager import AutoGenWorkFlowManager
import os


class AutoGenChatManager:
    def __init__(self) -> None:
        pass

    def chat(self, message: Message, history: List, flow_config: AgentWorkFlowConfig = None, **kwargs) -> None:
        work_dir = kwargs.get("work_dir", None)
        scratch_dir = os.path.join(work_dir, "scratch")
        os.makedirs(scratch_dir, exist_ok=True)
        os.environ['SCRATCH_DIR'] = scratch_dir
        print(f'scratch_dir {scratch_dir}')
        # if no flow config is provided, use the default
        if flow_config is None:
            flow_config = get_default_agent_config(scratch_dir)
        flow_config.session_id = message.session_id
        flow = AutoGenWorkFlowManager(config=flow_config, history=history, work_dir=scratch_dir, clear_work_dir=False)
        message_text = message.content.strip()

        output = ""
        start_time = time.time()

        metadata = {}
        flow.run(message=f"{message_text}", clear_history=False)

        metadata["messages"] = flow.agent_history

        output = ""

        if flow_config.summary_method == "last":
            successful_code_blocks = extract_successful_code_blocks(flow.agent_history)
            last_message = flow.agent_history[-1]["message"]["content"] if flow.agent_history else ""
            # if termination and seperated message then the one we care about is the previous message with the answer
            if "TERMINATE" in last_message and len(last_message) <= 10:
                last_message = flow.agent_history[-2]["message"]["content"] if flow.agent_history else ""
            successful_code_blocks = "\n\n".join(successful_code_blocks)
            output = (last_message + "\n" + successful_code_blocks) if successful_code_blocks else last_message
        elif flow_config.summary_method == "llm":
            output = flow.sender._summarize_chat(
                "reflection_with_llm",
                flow.receiver
            )
            successful_code_blocks = extract_successful_code_blocks(flow.agent_history)
            successful_code_blocks = "\n\n".join(successful_code_blocks)
            output = (output + "\n" + successful_code_blocks) if successful_code_blocks else output
        elif flow_config.summary_method == "none":
            output = ""

        metadata["code"] = ""
        metadata["summary_method"] = flow_config.summary_method
        end_time = time.time()
        metadata["time"] = end_time - start_time
        modified_files = get_modified_files(start_time, end_time, scratch_dir, dest_dir=work_dir)
        metadata["files"] = modified_files

        print("Modified files: ", len(modified_files))

        output_message = Message(
            user_id=message.user_id,
            root_msg_id=message.root_msg_id,
            role="assistant",
            content=output,
            metadata=json.dumps(metadata),
            session_id=message.session_id,
        )

        return output_message
