import json
import asyncio
import time
from typing import Any, List, Dict, Optional
import warnings
import websockets
from .datamodel import AgentWorkFlowConfig, Message, SocketMessage
from .utils import extract_successful_code_blocks, get_modified_files, summarize_chat_history
from .workflowmanager import AutoGenWorkFlowManager
import os
from dotenv import load_dotenv, find_dotenv
from fastapi import WebSocket, WebSocketDisconnect

class AutoGenChatManager:
    """
    This class handles the automated generation and management of chat interactions
    using an automated workflow configuration and message queue.
    """

    def __init__(self, websocket_manager) -> None:
        """
        Initializes the AutoGenChatManager with a message queue.

        :param websocket_manager: A websocket_manager to use for sending messages asynchronously.
        """
        self.websocket_manager = websocket_manager

    async def send(self, message: str) -> None:
        """
        Sends a message by putting it into the message queue.

        :param message: The message string to be sent.
        """
        if self.websocket_manager is not None:
            for connection in self.websocket_manager.active_connections:
                socket_client_id = self.websocket_manager.socket_store[connection]
                if message["connection_id"] == socket_client_id:
                    await self.websocket_manager.send_message(message, connection)

    async def chat(self, message: Message,
             flow_config: Optional[AgentWorkFlowConfig] = None,
             connection_id: Optional[str] = None, **kwargs) -> Message:
        """
        Processes an incoming message according to the agent's workflow configuration
        and generates a response.

        :param message: An instance of `Message` representing an incoming message.
        :param history: A list of dictionaries, each representing a past interaction.
        :param flow_config: An instance of `AgentWorkFlowConfig`. If None, defaults to a standard configuration.
        :param connection_id: An optional connection identifier.
        :param kwargs: Additional keyword arguments.
        :return: An instance of `Message` representing a response.
        """
        work_dir = kwargs.get("work_dir", None)
        if work_dir is None:
            raise ValueError("work_dir must be specified")

        scratch_dir = os.path.join(work_dir, "scratch")
        os.makedirs(scratch_dir, exist_ok=True)
        os.environ['SCRATCH_DIR'] = scratch_dir
        load_dotenv(find_dotenv(usecwd=True))
        # if no flow config is provided, use the default
        if flow_config is None:
            raise ValueError("flow_config must be specified")
        flow = AutoGenWorkFlowManager(
            config=flow_config, work_dir=scratch_dir, clear_work_dir=False,
            session_id=message.session_id, send_message_function=self.send, connection_id=connection_id, 
        )

        message_text = message.content.strip()

        start_time = time.time()
        await flow.run(message=f"{message_text}", clear_history=False)
        end_time = time.time()

        metadata = {
            "messages": flow.agent_history,
            "summary_method": flow_config.summary_method,
            "time": end_time - start_time,
            "code": "",  # Assuming that this is intentionally left empty
            "files": get_modified_files(start_time, end_time, scratch_dir, dest_dir=work_dir)
        }

        print("Modified files: ", len(metadata["files"]))
        agent_history = flow.agent_history.copy()
        metadata["messages"] = agent_history
        output, summary_method = self._generate_output(message_text, flow, agent_history, flow_config)
        metadata["summary_method"] = summary_method
        output_message = Message(
            user_id=message.user_id,
            root_msg_id=message.root_msg_id,
            role="assistant",
            content=output,
            metadata=json.dumps(metadata),
            session_id=message.session_id,
        )

        return output_message
    

    def _generate_output(self, message_text: str, flow: AutoGenWorkFlowManager, agent_history: list,
                         flow_config: AgentWorkFlowConfig):
        """
        Generates the output response based on the workflow configuration and agent history.

        :param message_text: The text of the incoming message.
        :param flow: An instance of `AutoGenWorkFlowManager`.
        :param flow_config: An instance of `AgentWorkFlowConfig`.
        :return: The output response as a string.
        """
        output_msg = ""
        summary_method = flow_config.summary_method
        if summary_method == "llm":
            model = flow.config.receiver.config.llm_config.config_list[0]
            status_message = SocketMessage(
                type="agent_status",
                data={"status": "summarizing",
                      "message": "Generating summary of agent dialogue"},
                connection_id=flow.connection_id
            )
            self.send(status_message.dict())
            output = summarize_chat_history(
                task=message_text, messages=agent_history, model=model)
            print("Output: ", output)
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

        return output_msg, summary_method


class WebSocketConnectionManager:
    """
    Manages WebSocket connections including sending, broadcasting, and managing the lifecycle of connections.
    """

    def __init__(self, active_connections: List[WebSocket] = None) -> None:
        """
        Initializes WebSocketConnectionManager with an optional list of active WebSocket connections.

        :param active_connections: A list of WebSocket objects representing the current active connections.
        """
        if active_connections is None:
            active_connections = []
        self.active_connections: List[WebSocket] = active_connections
        self.socket_store: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """
        Accepts a new WebSocket connection and appends it to the active connections list.

        :param websocket: The WebSocket instance representing a client connection.
        :param client_id: A string representing the unique identifier of the client.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        self.socket_store[websocket] = client_id
        print(
            f"New Connection: {client_id}, Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Disconnects and removes a WebSocket connection from the active connections list.

        :param websocket: The WebSocket instance to remove.
        """
        try:
            self.active_connections.remove(websocket)
            del self.socket_store[websocket]
            print(f"Connection Closed. Total: {len(self.active_connections)}")
        except ValueError:
            print("Error: WebSocket connection not found")

    def disconnect_all(self) -> None:
        """
        Disconnects all active WebSocket connections.
        """
        for connection in self.active_connections[:]:
            self.disconnect(connection)

    async def send_message(self, message: Dict, websocket: WebSocket) -> None:
        """
        Sends a JSON message to a single WebSocket connection.

        :param message: A JSON serializable dictionary containing the message to send.
        :param websocket: The WebSocket instance through which to send the message.
        """
        try:
            await websocket.send_json(message)
        except WebSocketDisconnect:
            print("Error: Tried to send a message to a closed WebSocket")
            self.disconnect(websocket)
        except websockets.exceptions.ConnectionClosedOK:
            print("Error: WebSocket connection closed normally")
            self.disconnect(websocket)

    async def broadcast(self, message: str) -> None:
        """
        Broadcasts a text message to all active WebSocket connections.

        :param message: A string containing the message to broadcast.
        """
        for connection in self.active_connections[:]:
            try:
                if connection.client_state == websockets.protocol.State.OPEN:
                    await connection.send_text(message)
                else:
                    print("Error: WebSocket connection is closed")
                    self.disconnect(connection)
            except WebSocketDisconnect:
                print("Error: Tried to send a message to a closed WebSocket")
                self.disconnect(connection)
            except websockets.exceptions.ConnectionClosedOK:
                print("Error: WebSocket connection closed normally")
                self.disconnect(connection)
