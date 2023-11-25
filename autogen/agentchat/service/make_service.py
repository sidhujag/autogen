from .. import GroupChatManager
from ..contrib.gpt_assistant_agent import GPTAssistantAgent
from ..service.backend_service import BaseFunction
from typing import Dict, Any, Optional
import requests
class MakeService:
    
    AGENT_REGISTRY: dict[str, GPTAssistantAgent] = {}
    GROUP_REGISTRY: dict[str, GroupChatManager] = {}
    FUNCTION_REGISTRY: dict[str, BaseFunction] = {}
    @staticmethod
    def get_service(service_type):
        from . import AgentService, FunctionsService, GroupService
        if service_type == 'agent':
            return AgentService()
        elif service_type == 'function':
            return FunctionsService()
        elif service_type == 'group':
            return GroupService()

    @staticmethod
    def _get_short_description(full_description: str) -> str:
        return (full_description[:640] + '...') if len(full_description) > 640 else full_description

    @staticmethod
    def call_api_url(sender, url: str, method: str, params: Optional[Dict[str, Any]] = None, body: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Makes an HTTP request to the specified URL with given parameters and body.

        Args:
        - url (str): The URL to which the request is sent.
        - method (str): HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
        - params (Optional[Dict[str, Any]]): URL parameters for GET requests.
        - body (Optional[Dict[str, Any]]): Data payload for POST, PUT, PATCH requests.
        - headers (Optional[Dict[str, str]]): HTTP headers.
        - timeout (int): Timeout for the request in seconds.

        Returns:
        - Dict[str, Any]: Response from the server.
        """
        try:
            response = requests.request(method=method, url=url, params=params, json=body, headers=headers, timeout=timeout)

            # Check if the response was successful
            response.raise_for_status()

            return {
                "status_code": response.status_code,
                "headers": response.headers,
                "body": response.json()
            }

        except requests.exceptions.HTTPError as errh:
            return {"error": f"HTTP Error: {errh}"}
        except requests.exceptions.ConnectionError as errc:
            return {"error": f"Error Connecting: {errc}"}
        except requests.exceptions.Timeout as errt:
            return {"error": f"Timeout Error: {errt}"}
        except requests.exceptions.RequestException as err:
            return {"error": f"Request Error: {err}"}