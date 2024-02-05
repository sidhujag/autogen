from typing import Optional, List, Dict, Any
import os
import json
import requests
from .datamodel import AgentConfig, AgentFlowSpec, LLMConfig, Skill
from .workflowmanager import AutoGenWorkFlowManager

class AgentService:
    @staticmethod
    def fetch_json(url, payload=None, method="GET"):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        try:
            if method == "POST":
                response = requests.post(url, json=payload, headers=headers)
            elif method == "GET":
                response = requests.get(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code == 200:
                return response.json()
            else:
                # Attempt to parse the response body for additional details
                try:
                    error_details = response.json()  # Assuming the error response is in JSON format
                except ValueError:
                    # If response is not in JSON format, use the raw text
                    error_details = response.text
                return {"status": False, "message": f"{response.reason}: {error_details}"}
        except Exception as e:
            return {"status": False, "message": str(e)}


    @staticmethod
    def fetch_skills(skill_ids: List[str]) -> List[Skill]:
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        skills: List[Skill] = []
        for skill_id in skill_ids:
            url = f"{server_url}/skill/{skill_id}"
            response = AgentService.fetch_json(url, method="GET")
            if response.get("status"):
                skills.append(Skill(**response.get("data")))
            else:
                print(f"Skill {skill_id} not found or error occurred. Skipping.")
        return skills

    @staticmethod
    def discover_skills(queries: List[str]) -> str:
        # Construct payload for API request
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/discover_skills"
        payload = {
            "user_id": os.getenv("USER_EMAIL", "guestuser@gmail.com"),
            "tags": queries
        }
        # Send request to create or update agent
        response = AgentService.fetch_json(url, payload, method="POST")
        return response
    
    @staticmethod
    def manage_agent_skills(agent_id: str, skill_ids: List[str], action: str) -> str:
        fetched_skills = AgentService.fetch_skills(skill_ids) if skill_ids else []
        assistant = AgentService.fetch_agent(agent_id)
        if not assistant:
            return json.dumps({"error": f"Agent not found with the id {agent_id}"})

        if action == 'add':
            existing_skill_ids = {skill.id for skill in assistant.skills}
            # Add only new skills
            new_skills = [skill for skill in fetched_skills if skill.id not in existing_skill_ids]
            assistant.skills.extend(new_skills)
        elif action == 'remove':
            # Filter out skills to be removed
            assistant.skills = [skill for skill in assistant.skills if skill.id not in skill_ids]
        else:
            return json.dumps({"error": "Invalid action specified"})
        
        # Construct payload for API request
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/agents"
        payload = {
            "user_id": os.getenv("USER_EMAIL", "guestuser@gmail.com"),
            "agent": assistant.dict()
        }
        
        # Send request to create or update agent
        response = AgentService.fetch_json(url, payload, method="POST")
        if 'data' in response:
            find_agent = AgentService.find_matching_agent(response['data'], assistant.id, assistant.config.name, assistant.description)
            response.pop("data")
            if find_agent:
                response["data"] = AgentService.sanitize_agent_output(find_agent)
        return response

    @staticmethod
    def sanitize_agent_output(agent: AgentFlowSpec) -> AgentFlowSpec:
        sanitized_skills = [
            Skill(title=skill.title, id=skill.id, description=skill.description, content="<omitted>", file_name=skill.file_name)
            for skill in agent.skills
        ] if agent.skills else []

        sanitized_agent = AgentFlowSpec(
            type=agent.type,
            config=AgentConfig(
                name=agent.config.name,
                system_message="<omitted>",
            ),
            id=agent.id,
            skills=sanitized_skills,
            description="<omitted>"
        )
        return sanitized_agent
    
    @staticmethod
    def find_matching_agent(agents: Dict[str, Any], id: Optional[str], name: str, description: str) -> Optional[AgentFlowSpec]:
        for agent in agents:
            if id and agent["id"] == id:
                return AgentFlowSpec(**agent)
            if agent["description"] == description and agent["config"]["name"] == name:
                return AgentFlowSpec(**agent)
        return None
    
    @staticmethod
    def create_or_update_agent(
        id: Optional[str],
        name: Optional[str],
        msg: Optional[str],
        description: Optional[str],
    ) -> Dict[str, Any]:
        # Initialize or fetch existing assistant
        assistant = None
        if id:
            assistant = AgentService.fetch_agent(id)
        
        # Merge skills if assistant exists
        if assistant:
            if msg:
                assistant.config.system_message = msg
            if description:
                assistant.description = description
            if name:
                assistant.config.name = name
        else:
            # Create new assistant if it does not exist
            llm_config = LLMConfig(config_list=[{"model": "gpt-4-turbo-preview"}], temperature=0)
            assistant = AgentFlowSpec(
                type="assistant",
                config=AgentConfig(name=name, system_message=msg, llm_config=llm_config),
                description=description,
                id=id  # This should be generated if not provided
            )
        # Construct payload for API request
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/agents"
        payload = {
            "user_id": os.getenv("USER_EMAIL", "guestuser@gmail.com"),  # Dynamically fetch user email
            "agent": assistant.dict()
        }
        
        # Send request to create or update agent
        response = AgentService.fetch_json(url, payload, method="POST")
        if 'data' in response:
            find_agent = AgentService.find_matching_agent(response['data'], assistant.id, assistant.config.name, assistant.description)
            response.pop("data")
            if find_agent:
                response["data"] = AgentService.sanitize_agent_output(find_agent)
        return response

    @staticmethod
    def fetch_agent(id: str) -> AgentFlowSpec:
        """
        Fetches agent by id

        Args:
            id (str): agent ID

        Returns:
            List[Dict[str, Any]]: A list of skill details.
        """
        if not id:
            return None
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/agent/{id}"
        response = AgentService.fetch_json(url, method="GET")
        if response.get("status"):
            return AgentFlowSpec(**response.get("data"))
        else:
            print(f"Agent {id} not found or error occurred. Skipping.")
            return None
