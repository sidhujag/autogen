from typing import Optional, List, Dict, Any
import os
import json
import requests
from .datamodel import AgentConfig, AgentFlowSpec, LLMConfig, Skill, GroupChatConfig

class AgentHelperService:
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
    def fetch_skill(skill_id: str) -> Skill:
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/skill?id={skill_id}"
        response = AgentHelperService.fetch_json(url, method="GET")
        if response.get("status"):
            return Skill(**response.get("data"))
        elif response.get("message"):
            msg = response.get("message")
            print(f"Skill {skill_id} not found, error: {msg}. Skipping.")
        else:
            print(f"Skill {skill_id} not found or error occurred. Skipping.")
        return None
    
    @staticmethod
    def fetch_skills(skill_ids: List[str]) -> List[Skill]:
        skills: List[Skill] = []
        for skill_id in skill_ids:
            skill = AgentHelperService.fetch_skill(skill_id)
            if skill:
                skills.append(skill)
        return skills

    @staticmethod
    def fetch_agent(agent_id: str) -> AgentFlowSpec:
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/agent?id={agent_id}"
        response = AgentHelperService.fetch_json(url, method="GET")
        if response.get("status"):
            return AgentFlowSpec(**response.get("data"))
        elif response.get("message"):
            msg = response.get("message")
            print(f"Agent {agent_id} not found, error: {msg}. Skipping.")
        else:
            print(f"Agent {agent_id} not found or error occurred. Skipping.")
        return None
    
    @staticmethod
    def fetch_agents(agent_ids: List[str]) -> List[AgentFlowSpec]:
        agents: List[AgentFlowSpec] = []
        for agent_id in agent_ids:
            agent = AgentHelperService.fetch_agent(agent_id)
            if agent:
                agents.append(agent)
        return agents
    
    @staticmethod
    def sanitize_discover_services_output(service_type: str, response_data):
        sanitized_data = {}
        if service_type == "skills":
            for query, skills in response_data.items():
                sanitized_skills = [AgentHelperService.sanitize_skill_output(Skill(**skill)) for skill in skills]
                sanitized_data[query] = sanitized_skills
        elif service_type == "agents":
            for query, agents in response_data.items():
                sanitized_agents = [AgentHelperService.sanitize_agent_output(AgentFlowSpec(**agent)) for agent in agents]
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
        response = AgentHelperService.fetch_json(url, payload, method="POST")
        if 'data' in response:
            response["data"] = AgentHelperService.sanitize_discover_services_output(service_type, response["data"])
        else:
            response["data"] = ""
        return json.dumps(response)


    @staticmethod
    def sanitize_skill_output(skill: Skill):
        return {"title": skill.title, "skill_id": skill.id, "description": skill.description, "file_name": skill.file_name}
    
    @staticmethod
    def sanitize_agent_output(agent: AgentFlowSpec):
        sanitized_skills = [
            AgentHelperService.sanitize_skill_output(skill)
            for skill in agent.skills
        ] if agent.skills else []

        sanitized_agent = {
            "type": agent.type,
            "config": {
                "name": agent.config.name,
            },
            "agent_id": agent.id,
            "skills": sanitized_skills,
            "description": agent.config.description
        }
        if agent.type == "groupchat":
            sanitized_group_agents = [
                AgentHelperService.sanitize_agent_output(group_agent)
                for group_agent in agent.groupchat_config.agents
            ] if agent.groupchat_config.agents else []

            sanitized_group = {
                "agents": sanitized_group_agents,
                "admin_name": agent.groupchat_config.admin_name,
                "max_round": agent.groupchat_config.max_round,
                "speaker_selection_method": agent.groupchat_config.speaker_selection_method,
                "send_introductions": agent.groupchat_config.send_introductions,
            }
            sanitized_agent["groupchat_config"] = sanitized_group
     
        return sanitized_agent

    @staticmethod
    def find_matching_agent(agents: Dict[str, Any], agent_id: str) -> Optional[AgentFlowSpec]:
        for agent in agents:
            if agent["id"] == agent_id:
                return AgentFlowSpec(**agent)
        return None
    
    
    @staticmethod
    def find_matching_skill(skills: Dict[str, Any], agent_id: str) -> Optional[Skill]:
        for skill in skills:
            if id and skill["id"] == agent_id:
                return Skill(**skill)
        return None
    
   
    @staticmethod
    def upsert_skill(
        agent_id: str,
        title: Optional[str],
        content: Optional[str],
        examples: Optional[str],
        file_name: Optional[str],
        description: Optional[str],
    ):
        # Initialize or fetch existing skill
        skill = AgentHelperService.fetch_skill(agent_id)
        if skill:
            if title:
                skill.title = title
            if file_name:
                skill.file_name = file_name
            if content:
                skill.content = content
            if examples:
                skill.examples = examples
            if description:
                skill.description = description
        else:
            if not title:
                return json.dumps({"error": "Missing title for new skill"})
            if not file_name:
                return json.dumps({"error": "Missing file_name for new skill"})
            if not content:
                return json.dumps({"error": "Missing content for new skill"})
            if not examples:
                return json.dumps({"error": "Missing examples for new skill"})
            if not description:
                return json.dumps({"error": "Missing description for new skill"})
            skill = Skill(
                title=title,
                file_name=file_name,
                content=content,
                examples=examples,
                description=description,
            )
        # Construct payload for API request
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/skills"
        payload = {
            "user_id": os.getenv("USER_EMAIL", "guestuser@gmail.com"),  # Dynamically fetch user email
            "skill": skill.dict()
        }
        
        # Send request to create or update agent
        response = AgentHelperService.fetch_json(url, payload, method="POST")
        if 'data' in response:
            find_agent = AgentHelperService.find_matching_skill(response['data'], skill.id)
            response["data"] = ""
            if find_agent:
                response["data"] = AgentHelperService.sanitize_skill_output(find_agent)
        else:
            response["data"] = ""
        return json.dumps(response)

    @staticmethod
    def upsert_agent(
        agent_id: str,
        new_agent_type: Optional[str],
        init_code: Optional[str],
        name: Optional[str],
        system_message: Optional[str],
        description: Optional[str],
        skills: Optional[List[str]],
        remove_skills: Optional[List[str]],
        agents: Optional[List[str]],
        remove_agents: Optional[List[str]],
    ) -> Dict[str, Any]:
        # Initialize or fetch existing assistant
        assistant = AgentHelperService.fetch_agent(agent_id)
        if assistant:
            if system_message:
                assistant.config.system_message = system_message
            if description:
                assistant.config.description = description
            if name:
                assistant.config.name = name
            if init_code:
                assistant.init_code = init_code
            if skills:
                existing_skill_ids = {skill.id for skill in assistant.skills}
                # Add only new skills
                new_skill_ids = [add_skill_id for add_skill_id in skills if add_skill_id not in existing_skill_ids]
                fetched_new_skills = AgentHelperService.fetch_skills(new_skill_ids)
                assistant.skills.extend(fetched_new_skills)
            elif remove_skills:
                # Filter out skills to be removed
                assistant.skills = [skill for skill in assistant.skills if skill.id not in remove_skills]
            if assistant.type == "groupchat":
                if agents:
                    existing_agent_ids = {agent.id for agent in assistant.groupchat_config.agents}
                    # Add only new agents
                    new_agent_ids = [add_group_agent_id for add_group_agent_id in agents if add_group_agent_id not in existing_agent_ids]
                    fetched_new_agents = AgentHelperService.fetch_agents(new_agent_ids)
                    assistant.groupchat_config.agents.extend(fetched_new_agents)
                elif remove_agents:
                    # Filter out agents to be removed
                    assistant.groupchat_config.agents = [agent for agent in assistant.groupchat_config.agents if agent.id not in remove_agents]
        else:
            if not new_agent_type:
                new_agent_type = "agent"
            if not init_code:
                return json.dumps({"error": "Missing init_code for new agent"})
            if not name:
                return json.dumps({"error": "Missing name for new agent"})
            if not description:
                return json.dumps({"error": "Missing description for new agent"})
            if not system_message:
                return json.dumps({"error": "Missing system_message for new agent"})
            if new_agent_type != "groupchat" and new_agent_type != "agent":
                return json.dumps({"error": f"Invalid type ({new_agent_type}) specified, must be one of 'groupchat' or 'agent'"})
            fetched_skills = None
            if skills:
                fetched_skills = AgentHelperService.fetch_skills(skills)
                if not fetched_skills:
                    return json.dumps({"error": f"Could not fetch skills."})
            # Create new assistant if it does not exist
            llm_config = LLMConfig(config_list=[{"model": "gpt-4-turbo-preview"}], temperature=0)
            assistant = AgentFlowSpec(
                type=new_agent_type,
                init_code=init_code,
                skills=fetched_skills,
                config=AgentConfig(name=name, description=description, system_message=system_message, llm_config=llm_config),
            )
            if new_agent_type == "groupchat":
                fetched_agents = []
                if agents:
                    fetched_agents = AgentHelperService.fetch_agents(agents)
                assistant.groupchat_config=GroupChatConfig(agents=fetched_agents, admin_name=name)
        # Construct payload for API request
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')

        url = f"{server_url}/agents"
        payload = {
            "user_id": os.getenv("USER_EMAIL", "guestuser@gmail.com"),  # Dynamically fetch user email
            "agent": assistant.dict()
        }

        # Send request to create or update agent
        response = AgentHelperService.fetch_json(url, payload, method="POST")
        if 'data' in response:
            find_agent = AgentHelperService.find_matching_agent(response['data'], assistant.id)
            response["data"] = ""
            if find_agent:
                response["data"] = AgentHelperService.sanitize_agent_output(find_agent)
        else:
            response["data"] = ""
        return json.dumps(response)

    @staticmethod
    def fetch_agent(agent_id: str) -> AgentFlowSpec:
        """
        Fetches agent by id

        Args:
            id (str): agent ID

        Returns:
            List[Dict[str, Any]]: A list of agent details.
        """
        if not agent_id:
            return None
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/agent?id={agent_id}"
        response = AgentHelperService.fetch_json(url, method="GET")
        if response.get("status"):
            return AgentFlowSpec(**response.get("data"))
        elif response.get("message"):
            msg = response.get("message")
            print(f"Agent {agent_id} not found, error: {msg}. Skipping.")
        else:
            print(f"Agent {agent_id} not found or error occurred. Skipping.")
            return None