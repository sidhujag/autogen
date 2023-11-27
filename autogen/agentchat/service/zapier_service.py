from typing import Dict, Any, Optional
import requests
import json

class ZapierService:
    base_url: str = "https://actions.zapier.com"
    @staticmethod
    def call_api_url(url: str, method: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, body: Optional[Dict[str, Any]] = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Makes an HTTP request to the specified URL with given parameters

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
            response = requests.request(method=method, url=url, params=params, headers=headers, json=body, timeout=timeout)

            # Check if the response was successful
            response.raise_for_status()
            return {
                "status_code": response.status_code,
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

    @staticmethod
    def _format_headers(APIKEY: str) -> Dict[str, str]:
        """Format headers for requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        headers.update({"X-API-Key": APIKEY})
        return headers

    @staticmethod
    def zapier_api_check(sender, APIKEY: str) -> str:
        return json.dumps(ZapierService.call_api_url(url=ZapierService.base_url + "/api/v1/check/", method="GET", headers=ZapierService._format_headers(APIKEY)))
    
    @staticmethod
    def zapier_api_get_configuration_link(sender, APIKEY: str) -> str:
        return json.dumps(ZapierService.call_api_url(url=ZapierService.base_url + "/api/v1/configuration-link/", method="GET", headers=ZapierService._format_headers(APIKEY)))
    
    @staticmethod
    def zapier_api_list_exposed_actions(sender, APIKEY: str) -> str:
        return json.dumps(ZapierService.call_api_url(url=ZapierService.base_url + "/api/v1/exposed/", method="GET", headers=ZapierService._format_headers(APIKEY)))
    
    @staticmethod
    def zapier_api_execute_action(sender, APIKEY: str, exposed_app_action_id: str, action_parameters: str, preview_only: bool = False) -> str:
        try:
            parameters_dict = json.loads(action_parameters)  # Parse the JSON string
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON format in action_parameters"})

        body = {"preview_only": preview_only, "instructions": "string"}
        body.update(parameters_dict)  # Merge the parameters into the body
        return json.dumps(ZapierService.call_api_url(url=ZapierService.base_url + f"/api/v1/exposed/{exposed_app_action_id}/execute/", method="POST", body=body, headers=ZapierService._format_headers(APIKEY)))
    
    @staticmethod
    def zapier_api_execute_log(sender, APIKEY: str, execution_log_id: str) -> str:
        return json.dumps(ZapierService.call_api_url(url=ZapierService.base_url + f"/api/v1/execution-log/{execution_log_id}/", method="GET", headers=ZapierService._format_headers(APIKEY)))
    
    @staticmethod
    def zapier_api_create_action(sender, configuration_link: str, action_description: str) -> str:
        action_url = f'{configuration_link}?setup_action={action_description}'
        return json.dumps({"success": f"Please tell the user to visit this URL to setup the action {action_url}. Then you can list the actions once user confirms to find the ID."})
    
    