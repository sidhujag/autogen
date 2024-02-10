from typing import Optional, List, Dict, Any
import os
import json
import requests
from .datamodel import AgentConfig, AgentFlowSpec, LLMConfig, Skill, Message, GroupChatConfig, GroupChatFlowSpec, AgentWorkFlowConfig, Session

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
        elif service_type == "workflows":
            for query, workflows in response_data.items():
                sanitized_workflows = [AgentService.sanitize_workflow_output(AgentWorkFlowConfig(**workflow)).dict() for workflow in workflows]
                sanitized_data[query] = sanitized_workflows
        else:
            raise ValueError("Invalid service type")

        return sanitized_data

    @staticmethod
    def discover_services(service_type: str, queries: List[str]) -> str:
        if service_type != "agents" and service_type != "skills" and service_type != "workflows":
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
            find_agent = AgentService.find_matching_agent(response['data'], assistant.id)
            response["data"] = ""
            if find_agent:
                response["data"] = AgentService.sanitize_agent_output(find_agent).dict()
        else:
            response["data"] = ""
        return json.dumps(response)

    @staticmethod
    def sanitize_skill_output(skill: Skill) -> Skill:
        return Skill(title=skill.title, id=skill.id, description=skill.description, content="<omitted>", file_name=skill.file_name)
    

    @staticmethod
    def sanitize_agent_output(agent: AgentFlowSpec) -> AgentFlowSpec:
        sanitized_skills = [
            AgentService.sanitize_skill_output(skill)
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
            description=agent.description
        )
        return sanitized_agent
    
    @staticmethod
    def sanitize_workflow_output(workflow: AgentWorkFlowConfig) -> AgentWorkFlowConfig:
        sanitized_sender = AgentService.sanitize_agent_output(workflow.sender)
        if workflow.receiver.type == "groupchat":
            sanitized_receiver = AgentService.sanitize_group_chat_flow_spec(workflow.receiver)
        else:
            sanitized_receiver = AgentService.sanitize_agent_output(workflow.receiver)
        
        sanitized_workflow = AgentWorkFlowConfig(
            name=workflow.name,
            sender=sanitized_sender,
            receiver=sanitized_receiver,
            type=workflow.type,
            id=workflow.id,
            summary_method=workflow.summary_method,
            description=workflow.description
        )
        return sanitized_workflow

    @staticmethod
    def sanitize_group_chat_flow_spec(group_chat_flow_spec: GroupChatFlowSpec) -> GroupChatFlowSpec:
        sanitized_agents = [
            AgentService.sanitize_agent_output(agent)
            for agent in group_chat_flow_spec.groupchat_config.agents
        ] if group_chat_flow_spec.groupchat_config and group_chat_flow_spec.groupchat_config.agents else []
        
        sanitized_group_chat_config = GroupChatConfig(
            agents=sanitized_agents,
            admin_name=group_chat_flow_spec.groupchat_config.admin_name if group_chat_flow_spec.groupchat_config else "Admin",
            messages=[],
            max_round=group_chat_flow_spec.groupchat_config.max_round if group_chat_flow_spec.groupchat_config else 10,
        )
        
        sanitized_group_chat_flow_spec = GroupChatFlowSpec(
            type="groupchat",
            config=AgentConfig(
                name=GroupChatFlowSpec.config.name,
                system_message="<omitted>",
            ),
            groupchat_config=sanitized_group_chat_config,
            id=group_chat_flow_spec.id,
            description=group_chat_flow_spec.description,
        )
        return sanitized_group_chat_flow_spec

    @staticmethod
    def find_matching_agent(agents: Dict[str, Any], id: str) -> Optional[AgentFlowSpec]:
        for agent in agents:
            if agent["id"] == id:
                return AgentFlowSpec(**agent)
        return None
    
    @staticmethod
    def sanitize_session_output(session: Session) -> Session:
        session.flow_config = AgentService.sanitize_workflow_output(session.flow_config)
        return session
    
    @staticmethod
    def find_matching_session(sessions: Dict[str, Any], id: str) -> Optional[Session]:
        for session in sessions:
            if session["id"] == id:
                return Session(**session)
        return None
    
    @staticmethod
    def find_matching_skill(skills: Dict[str, Any], id: str) -> Optional[Skill]:
        for skill in skills:
            if id and skill["id"] == id:
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
            find_agent = AgentService.find_matching_skill(response['data'], skill.id)
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
                description=description
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
            find_agent = AgentService.find_matching_agent(response['data'], assistant.id)
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

    @staticmethod
    def fetch_session(id: str) -> Session:
        """
        Fetches session by id

        Args:
            id (str): session ID

        Returns:
            List[Dict[str, Any]]: A list of session details.
        """
        if not id:
            return None
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/session?id={id}"
        response = AgentService.fetch_json(url, method="GET")
        if response.get("status"):
            return Session(**response.get("data"))
        elif response.get("message"):
            msg = response.get("message")
            print(f"Session {id} not found, error: {msg}. Skipping.")
        else:
            print(f"Session {id} not found or error occurred. Skipping.")
            return None
        
    @staticmethod
    def fetch_workflow(id: str) -> AgentWorkFlowConfig:
        """
        Fetches workflow by id

        Args:
            id (str): workflow ID

        Returns:
            List[Dict[str, Any]]: A list of workflow details.
        """
        if not id:
            return None
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/workflow?id={id}"
        response = AgentService.fetch_json(url, method="GET")
        if response.get("status"):
            return AgentWorkFlowConfig(**response.get("data"))
        elif response.get("message"):
            msg = response.get("message")
            print(f"Workflow {id} not found, error: {msg}. Skipping.")
        else:
            print(f"Workflow {id} not found or error occurred. Skipping.")
            return None
        
    @staticmethod
    def initiate_destination_session(
        workflow_id: str
    ) -> Dict[str, Any]:
     
        workflow = AgentService.fetch_workflow(workflow_id)
        if not workflow:
            return json.dumps({"error": f"Could not find workflow, id: {workflow_id}"})
        session = Session(user_id=os.getenv("USER_EMAIL", "guestuser@gmail.com"), flow_config=workflow.dict())
        # Construct payload for API request
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/sessions"
        payload = {
            "user_id": os.getenv("USER_EMAIL", "guestuser@gmail.com"),
            "session": session.dict()
        }
        
        # Send request to create or update agent
        response = AgentService.fetch_json(url, payload, method="POST")
        if 'data' in response:
            find_session = AgentService.find_matching_session(response['data'], session.id)
            response["data"] = ""
            if find_session:
                response["data"] = AgentService.sanitize_session_output(find_session).dict()
        else:
            response["data"] = ""
        return json.dumps(response)

    @staticmethod
    def send_message_to_destination_session(
        source_session_id: str,
        destination_session_id: str,
        message_content: str,
        message_type: str
    ) -> Dict[str, Any]:
        if message_type != "SEND" and message_type != "REPLY":
            return json.dumps({"error": f"Invalid message type {message_type}"})
        content = {
            "source_session_id": source_session_id,
            "destination_session_id": destination_session_id,
            "message_type": message_type,
        }
        if message_type != "SEND":
            content["message"] = f"Message being sent from source session to destination session (YOU) to request some information in a REPLY. After finishing please send another message with message_type=REPLY to the source session. Message request: {message_content}"
        elif message_type != "REPLY":
            content["message"] = f"Response from a request for information. Response: {message_content}"
        src_session = AgentService.fetch_session(source_session_id)
        if not src_session:
            return json.dumps({"error": f"Could not find source session, id: {source_session_id}"})
        session = AgentService.fetch_session(destination_session_id)
        if not session:
            return json.dumps({"error": f"Could not find destination session, id: {destination_session_id}"})
        workflow = AgentService.fetch_workflow(session.flow_config.id)
        if not workflow:
            return json.dumps({"error": f"Could not find workflow from destination session (destination_session_id), workflow id: {session.flow_config.id}"})
        
        message = Message(role="assistant", content=message_content, root_msg_id="0", session_id = destination_session_id, user_id=os.getenv("USER_EMAIL", "guestuser@gmail.com"))
        # Construct payload for API request
        server_url = os.getenv('GATSBY_API_URL', 'http://127.0.0.1:8080/api')
        url = f"{server_url}/messages"
        payload = {
            "message": message.dict(),
            "flow_config": workflow
        }
        
        # Send request to create or update agent
        response = AgentService.fetch_json(url, payload, method="POST")
        return json.dumps(response)