import base64
import json
import os
from pathlib import Path
import re
import uuid
from typing import Any, ClassVar, List, Union

from pydantic import Field


from ..agentchat.agent import LLMAgent
from .base import CodeBlock, CodeExecutor, CodeExtractor, CodeResult, IPythonCodeResult
from .markdown_code_extractor import MarkdownCodeExtractor
from .jupyter import JupyterConnectable, JupyterConnectionInfo, LocalJupyterServer, JupyterClient

__all__ = ("JupyterCodeExecutor", "LocalJupyterCodeExecutor")


class JupyterCodeExecutor(CodeExecutor):
    """(Experimental) A code executor class that executes code statefully using an embedded
    IPython kernel managed by this class.

    **This will execute LLM generated code on the local machine.**

    Each execution is stateful and can access variables created from previous
    executions in the same session. The kernel must be installed before using
    this class. The kernel can be installed using the following command:
    `python -m ipykernel install --user --name {kernel_name}`
    where `kernel_name` is the name of the kernel to install.

    Args:
        timeout (int): The timeout for code execution, by default 60.
        kernel_name (str): The kernel name to use. Make sure it is installed.
            By default, it is "python3".
        output_dir (str): The directory to save output files, by default ".".
        system_message_update (str): The system message update to add to the
            agent that produces code. By default it is
            `JupyterCodeExecutor.DEFAULT_SYSTEM_MESSAGE_UPDATE`.
    """

    DEFAULT_SYSTEM_MESSAGE_UPDATE: ClassVar[
        str
    ] = """
# IPython Coding Capability
You have been given coding capability to solve tasks using Python code in a stateful IPython kernel.
You are responsible for writing the code, and the user is responsible for executing the code.

When you write Python code, put the code in a markdown code block with the language set to Python.
For example:
```python
x = 3
```
You can use the variable `x` in subsequent code blocks.
```python
print(x)
```

Write code incrementally and leverage the statefulness of the kernel to avoid repeating code.
Import libraries in a separate code block.
Define a function or a class in a separate code block.
Run code that produces output in a separate code block.
Run code that involves expensive operations like download, upload, and call external APIs in a separate code block.

When your code produces an output, the output will be returned to you.
Because you have limited conversation memory, if your code creates an image,
the output will be a path to the image instead of the image itself.
"""

    class UserCapability:
        """(Experimental) An AgentCapability class that gives agent ability use a stateful
        IPython code executor. This capability can be added to an agent using
        the `add_to_agent` method which append a system message update to the
        agent's system message."""

        def __init__(self, system_message_update: str):
            self._system_message_update = system_message_update

        def add_to_agent(self, agent: LLMAgent) -> None:
            """Add this capability to an agent by appending a system message
            update to the agent's system message.

            **Currently we do not check for conflicts with existing content in
            the agent's system message.**

            Args:
                agent (LLMAgent): The agent to add the capability to.
            """
            agent.update_system_message(agent.system_message + self._system_message_update)

    def __init__(
        self,
        jupyter_server: Union[JupyterConnectable, JupyterConnectionInfo],
        kernel_name: str = "python3",
        timeout: int = 60,
        output_dir: Union[Path, str] = Path("."),
        system_message_update: str = DEFAULT_SYSTEM_MESSAGE_UPDATE,
    ):
        if timeout < 1:
            raise ValueError("Timeout must be greater than or equal to 1.")

        if isinstance(output_dir, str):
            output_dir = Path(output_dir)

        if not output_dir.exists():
            raise ValueError(f"Output directory {output_dir} does not exist.")

        if isinstance(jupyter_server, JupyterConnectable):
            self._connection_info = jupyter_server.connection_info
        elif isinstance(jupyter_server, JupyterConnectionInfo):
            self._connection_info = jupyter_server
        else:
            raise ValueError("jupyter_server must be a JupyterConnectable or JupyterConnectionInfo.")

        self._jupyter_client = JupyterClient(self._connection_info)
        available_kernels = self._jupyter_client.list_kernel_specs()
        if kernel_name not in available_kernels["kernelspecs"]:
            raise ValueError(f"Kernel {kernel_name} is not installed.")

        self._kernel_id = self._jupyter_client.start_kernel(kernel_name)
        self._kernel_name = kernel_name
        self._jupyter_kernel_client = self._jupyter_client.get_kernel_client(self._kernel_id)
        self._timeout = timeout
        self._output_dir = output_dir
        self._system_message_update = system_message_update

    @property
    def user_capability(self) -> "JupyterCodeExecutor.UserCapability":
        """(Experimental) Export a user capability for this executor that can be added to
        an agent using the `add_to_agent` method."""
        return JupyterCodeExecutor.UserCapability(self._system_message_update)

    @property
    def code_extractor(self) -> CodeExtractor:
        """(Experimental) Export a code extractor that can be used by an agent."""
        return MarkdownCodeExtractor()

    def execute_code_blocks(self, code_blocks: List[CodeBlock]) -> IPythonCodeResult:
        """(Experimental) Execute a list of code blocks and return the result.

        This method executes a list of code blocks as cells in an IPython kernel
        managed by this class.
        See: https://jupyter-client.readthedocs.io/en/stable/messaging.html
        for the message protocol.

        Args:
            code_blocks (List[CodeBlock]): A list of code blocks to execute.

        Returns:
            IPythonCodeResult: The result of the code execution.
        """
        self._jupyter_kernel_client.wait_for_ready()
        outputs = []
        output_files = []
        for code_block in code_blocks:
            code = self._process_code(code_block.code)
            result = self._jupyter_kernel_client.execute(code, timeout_seconds=self._timeout)
            if result.is_ok:
                outputs.append(result.output)
                for data in result.data_items:
                    if data.mime_type == "image/png":
                        path = self._save_image(data.data)
                        outputs.append(f"Image data saved to {path}")
                        output_files.append(path)
                    elif data.mime_type == "text/html":
                        path = self._save_html(data.data)
                        outputs.append(f"HTML data saved to {path}")
                        output_files.append(path)
                    else:
                        outputs.append(json.dumps(data.data))
            else:
                return IPythonCodeResult(
                    exit_code=1,
                    output=f"ERROR: {result.output}",
                )

        return IPythonCodeResult(
            exit_code=0, output="\n".join([str(output) for output in outputs]), output_files=output_files
        )

    def restart(self) -> None:
        """(Experimental) Restart a new session."""
        self._jupyter_client.restart_kernel(self._kernel_id)
        self._jupyter_kernel_client = self._jupyter_client.get_kernel_client(self._kernel_id)

    def _save_image(self, image_data_base64: str) -> str:
        """Save image data to a file."""
        image_data = base64.b64decode(image_data_base64)
        # Randomly generate a filename.
        filename = f"{uuid.uuid4().hex}.png"
        path = os.path.join(self._output_dir, filename)
        with open(path, "wb") as f:
            f.write(image_data)
        return os.path.abspath(path)

    def _save_html(self, html_data: str) -> str:
        """Save html data to a file."""
        # Randomly generate a filename.
        filename = f"{uuid.uuid4().hex}.html"
        path = os.path.join(self._output_dir, filename)
        with open(path, "w") as f:
            f.write(html_data)
        return os.path.abspath(path)

    def _process_code(self, code: str) -> str:
        """Process code before execution."""
        # Find lines that start with `! pip install` and make sure "-qqq" flag is added.
        lines = code.split("\n")
        for i, line in enumerate(lines):
            # use regex to find lines that start with `! pip install` or `!pip install`.
            match = re.search(r"^! ?pip install", line)
            if match is not None:
                if "-qqq" not in line:
                    lines[i] = line.replace(match.group(0), match.group(0) + " -qqq")
        return "\n".join(lines)


class LocalJupyterCodeExecutor(JupyterCodeExecutor):
    def __init__(self, **kwargs: Any):
        """Creates a LocalJupyterServer and passes it to JupyterCodeExecutor, see JupyterCodeExecutor for args"""
        jupyter_server = LocalJupyterServer()
        super().__init__(jupyter_server=jupyter_server, **kwargs)
