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
            url = f"{server_url}/skill?id={skill_id}"
            response = AgentService.fetch_json(url, method="GET")
            if response.get("status"):
                skills.append(Skill(**response.get("data")))
            elif response.get("message"):
                msg = response.get("message")
                print(f"Skill {skill_id} not found, error: {msg}. Skipping.")
            else:
                print(f"Skill {skill_id} not found or error occurred. Skipping.")
        return skills

    @staticmethod
    def sanitize_discover_services_output(service_type: str, response_data):
        sanitized_data = {}
        if service_type == "skills":
            for query, skills in response_data.items():
                sanitized_skills = [AgentService.sanitize_skill_output(Skill(**skill)).dict() for skill in skills]
                sanitized_data[query] = sanitized_skills
        elif service_type == "agents":
            for query, agents in response_data.items():
                sanitized_agents = [AgentService.sanitize_agent_output(AgentFlowSpec(**agent)).dict() for agent in agents]
                sanitized_data[query] = sanitized_agents
        else:
            raise ValueError("Invalid service type")

        return sanitized_data

    @staticmethod
    def discover_services(service_type: str, queries: List[str]) -> str:
        if service_type != "agents" and service_type != "skills":
            return json.dumps({"error": f"Invalid service type: {service_type}"})
        # Construct payload for API request
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/discover_services"
        payload = {
            "user_id": os.getenv("USER_EMAIL", "guestuser@gmail.com"),
            "msg_id": service_type,
            "tags": queries
        }
        # Send request to discover service
        response = AgentService.fetch_json(url, payload, method="POST")
        if 'data' in response:
            response["data"] = AgentService.sanitize_discover_services_output(service_type, response["data"])
        else:
            response["data"] = ""
        return json.dumps(response)

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
            response["data"] = ""
            if find_agent:
                response["data"] = AgentService.sanitize_agent_output(find_agent).dict()
        else:
            response["data"] = ""
        return json.dumps(response)

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
    def sanitize_skill_output(skill: Skill) -> Skill:
        return Skill(title=skill.title, id=skill.id, description=skill.description, content="<omitted>", file_name=skill.file_name)
    
    @staticmethod
    def find_matching_skill(skills: Dict[str, Any], id: Optional[str], file_name: str, content: str) -> Optional[Skill]:
        for skill in skills:
            if id and skill["id"] == id:
                return Skill(**skill)
            if skill["file_name"] == file_name and skill["content"] == content:
                return Skill(**skill)
        return None
    
    @staticmethod
    def create_or_update_skill(
        id: Optional[str],
        title: Optional[str],
        content: Optional[str],
        file_name: Optional[str],
        description: Optional[str],
    ):
        # Initialize or fetch existing skill
        skill = None
        if id:
            skill = AgentService.fetch_skills([id])
        
        if skill:
            skill = skill[0]
            if title:
                skill.title = title
            if file_name:
                skill.file_name = file_name
            if content:
                skill.content = content
            if description:
                skill.description = description
        else:
            skill = Skill(
                title=title,
                file_name=file_name,
                content=content,
                description=description,
                id=id  # This should be generated if not provided
            )
        # Construct payload for API request
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/skills"
        payload = {
            "user_id": os.getenv("USER_EMAIL", "guestuser@gmail.com"),  # Dynamically fetch user email
            "skill": skill.dict()
        }
        
        # Send request to create or update agent
        response = AgentService.fetch_json(url, payload, method="POST")
        if 'data' in response:
            find_agent = AgentService.find_matching_skill(response['data'], skill.id, skill.file_name, skill.content)
            response["data"] = ""
            if find_agent:
                response["data"] = AgentService.sanitize_skill_output(find_agent).dict()
        else:
            response["data"] = ""
        return json.dumps(response)

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
            response["data"] = ""
            if find_agent:
                response["data"] = AgentService.sanitize_agent_output(find_agent).dict()
        else:
            response["data"] = ""
        return json.dumps(response)

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
        url = f"{server_url}/agent?id={id}"
        response = AgentService.fetch_json(url, method="GET")
        if response.get("status"):
            return AgentFlowSpec(**response.get("data"))
        elif response.get("message"):
            msg = response.get("message")
            print(f"Agent {id} not found, error: {msg}. Skipping.")
        else:
            print(f"Agent {id} not found or error occurred. Skipping.")
            return None
