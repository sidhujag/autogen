
from typing import Optional
import autogen
from .datamodel import AgentConfig, AgentFlowSpec, LLMConfig, Skill
import os
from typing import List, Dict, Any
import requests
class AgentService:
    @staticmethod
    def fetch_json(url, payload, method="POST"):
        try:
            if method == "POST":
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": False, "message": response.reason}
            elif method == "GET":
                headers = {
                    "Content-Type": "application/json",
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": False, "message": response.reason}
        except Exception as e:
            return {"status": False, "message": str(e)}
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
        server_url = os.getenv('GATSBY_API_URL', '/api')
        url = f"{server_url}/agent/{id}"
        response = AgentService.fetch_json(url, method="GET")
        if response.get("status"):
            return AgentFlowSpec(**response.get("data"))
        else:
            print(f"Agent {id} not found or error occurred. Skipping.")
            return None
    @staticmethod
    def fetch_skills(skill_ids: List[str]) -> List[Skill]:
        """
        Fetches skills from a list of skill IDs by using the fetch_json function.

        Args:
            skill_ids (List[str]): A list of skill IDs.

        Returns:
            A list of skills.
        """
        server_url = os.getenv('GATSBY_API_URL', '/api')
        skills:List[Skill] = []
        for skill_id in skill_ids:
            url = f"{server_url}/skill/{skill_id}"
            # Assuming fetch_json can be used for GET request as well
            response = AgentService.fetch_json(url, method="GET")
            if response.get("status"):
                skills.append(Skill(**response.get("data")))
            else:
                print(f"Skill {skill_id} not found or error occurred. Skipping.")
        return skills
    @staticmethod
    def create_or_update_agent(
        id: Optional[str],
        name: Optional[str],
        msg: Optional[str],
        skill_ids: Optional[List[str]],
        description: Optional[str],
    ) -> Dict[str, Any]:
        """
        Updated version to fetch full skill data based on skill IDs before creating or updating an agent.
        """

        skills:List[Skill] = AgentService.fetch_skills(skill_ids) if skill_ids else []
        assistant:AgentFlowSpec = AgentService.fetch_agent(id)
        if assistant:
            if msg:
                assistant.config.system_message = autogen.AssistantAgent.DEFAULT_SYSTEM_MESSAGE + "\n\n" + msg
            if skill_ids:
                skills.extend(skills)
            if description:
                assistant.description = description
            if name:
                assistant.config.name = name
        else:
            llm_config = LLMConfig(
                config_list=[{"model": "gpt-4-turbo-preview"}],
                temperature=0,
            )
            assistant = AgentFlowSpec(
                type="assistant",
                config=AgentConfig(
                    name=name,
                    system_message=autogen.AssistantAgent.DEFAULT_SYSTEM_MESSAGE,
                    llm_config=llm_config,
                ),
                skills=skills,
                description=description
            )
            if msg:
                assistant.config.system_message = autogen.AssistantAgent.DEFAULT_SYSTEM_MESSAGE + "\n\n" + msg

        payload = {
            "user_id": "guestuser@gmail.com",
            "agent": assistant.dict()
        }
        server_url = os.getenv('GATSBY_API_URL', '/api')
        url = f"{server_url}/agents"
        return AgentService.fetch_json(url, payload, method="POST")
