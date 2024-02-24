from __future__ import annotations
from types import TracebackType

from typing import Optional, Union, cast
import subprocess
import signal
import sys
import json
import secrets
import socket
import atexit

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from .base import JupyterConnectable, JupyterConnectionInfo
from .jupyter_client import JupyterClient


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return cast(int, s.getsockname()[1])


class LocalJupyterServer(JupyterConnectable):
    class GenerateToken:
        pass

    def __init__(
        self,
        ip: str = "127.0.0.1",
        port: Optional[int] = None,
        token: Union[str, GenerateToken] = GenerateToken(),
        log_file: str = "jupyter_gateway.log",
        log_level: str = "INFO",
        log_max_bytes: int = 1048576,
        log_backup_count: int = 3,
    ):
        # Remove as soon as https://github.com/jupyter-server/kernel_gateway/issues/398 is fixed
        if sys.platform == "win32":
            raise ValueError("LocalJupyterServer is not supported on Windows due to kernelgateway bug.")

        # Check Jupyter gateway server is installed
        try:
            subprocess.run(
                [sys.executable, "-m", "jupyter", "kernelgateway", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError:
            raise ValueError(
                "Jupyter gateway server is not installed. Please install it with `pip install jupyter_kernel_gateway`."
            )

        self.ip = ip
        if port is None:
            port = _get_free_port()
        self.port = port

        if isinstance(token, LocalJupyterServer.GenerateToken):
            token = secrets.token_hex(32)

        self.token = token
        logging_config = {
            "handlers": {
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": log_level,
                    "maxBytes": log_max_bytes,
                    "backupCount": log_backup_count,
                    "filename": log_file,
                }
            },
            "loggers": {"KernelGatewayApp": {"level": log_level, "handlers": ["file", "console"]}},
        }

        # Run Jupyter gateway server with detached subprocess
        args = [
            sys.executable,
            "-m",
            "jupyter",
            "kernelgateway",
            "--KernelGatewayApp.ip",
            ip,
            "--KernelGatewayApp.port",
            str(port),
            "--KernelGatewayApp.auth_token",
            token,
            "--JupyterApp.answer_yes",
            "true",
            "--JupyterApp.logging_config",
            json.dumps(logging_config),
            "--JupyterWebsocketPersonality.list_kernels",
            "true",
        ]
        self._subprocess = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Satisfy mypy, we know this is not None because we passed PIPE
        assert self._subprocess.stderr is not None
        # Read stderr until we see "is available at" or the process has exited with an error
        stderr = ""
        while True:
            result = self._subprocess.poll()
            if result is not None:
                stderr += self._subprocess.stderr.read()
                print(f"token=[[[[{token}]]]]")
                raise ValueError(f"Jupyter gateway server failed to start with exit code: {result}. stderr:\n{stderr}")
            line = self._subprocess.stderr.readline()
            stderr += line
            if "is available at" in line:
                break

        # Poll the subprocess to check if it is still running
        result = self._subprocess.poll()
        if result is not None:
            raise ValueError(
                f"Jupyter gateway server failed to start. Please check the logs ({log_file}) for more information."
            )

        atexit.register(self.stop)

    def stop(self) -> None:
        if self._subprocess.poll() is None:
            if sys.platform == "win32":
                self._subprocess.send_signal(signal.CTRL_C_EVENT)
            else:
                self._subprocess.send_signal(signal.SIGINT)
            self._subprocess.wait()

    @property
    def connection_info(self) -> JupyterConnectionInfo:
        return JupyterConnectionInfo(host=self.ip, use_https=False, port=self.port, token=self.token)

    def get_client(self) -> JupyterClient:
        return JupyterClient(self.connection_info)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        self.stop()
