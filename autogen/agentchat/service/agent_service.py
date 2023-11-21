from .. import GroupChatManager
from ..contrib.gpt_assistant_agent import GPTAssistantAgent
from typing import List
from autogen.agentchat.service.function_specs import management_function_specs, group_info_function_specs, files_function_specs
import json
import requests
import openai

class AgentService:
    BASIC_AGENT_SYSTEM_MESSAGE: str = """
Agent Details: Name: {agent_name}, Description: {agent_description}, Group: {group_name}{dependent}, Capabilities: {capabilities}

{capability_instruction}

As a Basic Agent, your role is to collaborate effectively with your peers, utilizing your unique skills to achieve common goals. When faced with complex tasks, plan meticulously, assigning roles to suitable agents or groups. You cannot update agents or groups but you can update functions. Functions are used within agents which are used withing groups. You can tag the manager in your group through text-interaction to have agents/groups modified. Strive for comprehensive and creative solutions, focusing on the task at hand. Prioritize reusing existing functions, agents, and groups. If a specific function is requested, first check its availability. If it's not available, communicate this clearly and suggest alternatives. Terminate groups judiciously based on the conversation's progress and relevance, avoiding circular discussions or repeated statements. Be cautious with non-accepted functions; if you do choose them then repair them rather than creating new versions. Prefer to use accepted functions over non-accepted. Always consider the group's message history in your responses.

Ensure to review the group's message history thoroughly before initiating a redundant action. Additionally, if the context indicates that a request has been previously addressed, you will acknowledge and proceed from the most recent state of information.

Your environment HAS access to real-time information and the internet through your discovery process. Read each function you have been give carefully to discover and enhance your abilities.

Terminate if conversation is going in circles.

Include speaker/group in the assistant message just like the user messages in 'speaker (to group)' format.

Custom Instructions: {custom_instructions}
"""

    MANAGER_AGENT_SYSTEM_MESSAGE: str = """
Agent Details: Name: {agent_name}, Description: {agent_description}, Group: {group_name}{dependent}, Capabilities: {capabilities}

{capability_instruction}

As a Manager Agent, you are tasked with leading and coordinating group activities. Develop comprehensive strategies, assign tasks effectively, and utilize your management tools for optimal problem-solving. Encourage focus and creativity within your team. Functions are used within agents which are used withing groups. When a specific function is requested, first attempt to access or add it. If this is not possible, provide a clear explanation and suggest viable alternatives. Terminate groups judiciously based on the conversation's progress and relevance, avoiding circular discussions or repeated statements. Avoid creating new entities if existing ones are adequate. Be wary of non-accepted functions and aim to improve them if you do choose them. Prefer to use accepted functions over non-accepted. Ensure your responses reflect the group's message history.

Ensure to review the group's message history thoroughly before initiating a redundant action. Additionally, if the context indicates that a request has been previously addressed, you will acknowledge and proceed from the most recent state of information.

Watch for others tagging you in the chat for certain requests like modifying agents and groups only you can fulfill.

Your environment HAS access to real-time information and the internet through your discovery process. Read each function you have been give carefully to discover and enhance your abilities.

Terminate if conversation is going in circles.

Include speaker/group in the assistant message just like the user messages in 'speaker (to group)' format.

Custom Instructions: {custom_instructions}

Group Stats: {group_stats}
"""

    CAPABILITY_SYSTEM_MESSAGE: str = """Agent Capability Breakdown:
- INFO: Access and manage information on functions, agents, and groups, including termination of groups. Discover entities.
- CODE_INTERPRETER: Additional ability to write and run Python code. Use OpenAI interpreter for OpenAI files, and local interpreter for local files and internet access. Invoke local interpreter through and custom functions. Execute functions in your context.
- RETRIEVAL: Additional ability to enhance knowledge with external documents and data using files.
- FILES: Additional ability to manage files for data processing and sharing.
- MANAGEMENT: Additional ability to modify agents/groups, communicate across groups to manage group activities.
"""

    @staticmethod
    def get_agent(agent_model) -> GPTAssistantAgent:
        from . import BackendService, MakeService
        agent: GPTAssistantAgent = MakeService.AGENT_REGISTRY.get(agent_model.name)
        if agent is None:
            backend_agents, err = BackendService.get_backend_agents([agent_model])
            if err is None and len(backend_agents) > 0:
                agent, err = AgentService.make_agent(backend_agents[0])
                if err is not None:
                    MakeService.AGENT_REGISTRY[agent_model.name] = agent
        return agent

    @staticmethod
    def discover_agents(sender: GPTAssistantAgent, query: str, category: str = None) -> str:
        from . import BackendService, DiscoverAgentsModel
        if sender is None:
            return json.dumps({"error": "Sender not found"})
        response, err = BackendService.discover_backend_agents(DiscoverAgentsModel(auth=sender.auth, query=query,category=category))
        if err is not None:
            return err
        return response

    @staticmethod
    def get_agent_info(sender: GPTAssistantAgent, name: str) -> str:
        from . import GetAgentModel, AgentService, FunctionsService, GetFunctionModel, AgentInfo, FunctionInfo
        if sender is None:
            return json.dumps({"error": "Sender not found"})
        agent = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=name))
        if agent is None:
            return json.dumps({"error": f"Agent({name}) not found"})

        function_models = [GetFunctionModel(auth=sender.auth, name=function_name) for function_name in agent.function_names]
        functions = FunctionsService.get_functions(function_models)

        # Convert BaseFunction objects to FunctionInfo objects
        function_info_list = [FunctionInfo(name=func.name, status=func.status) for func in functions]

        agentInfo = AgentInfo(
            name=agent.name,
            description=agent.description,
            system_message=agent.system_message,
            capability=agent.capability,
            files=agent.files,
            functions=function_info_list
        )
        return json.dumps({"response": agentInfo.dict()})

    
    @staticmethod
    def upsert_agent(sender: GPTAssistantAgent, name: str, description: str = None, custom_instructions: str = None, functions_to_add: List[str] = None,  functions_to_remove: List[str] = None, category: str = None, capability: int = 1) -> str: 
        from . import UpsertAgentModel, INFO, GetAgentModel, FunctionsService, GetFunctionModel
        if sender is None:
            return json.dumps({"error": "Sender not found"})
        if not capability & INFO:
            return json.dumps({"error": "INFO bit must be set for capability"})
        agent = AgentService.get_agent(GetAgentModel(auth=sender.auth, name=name))
        id = None
        created_assistant = False
        if agent is None:
            created_assistant = True
            # place holder to get assistant id
            openai_assistant = sender.openai_client.beta.assistants.create(
                name=name,
                instructions="",
                tools=[],
                model="gpt-4-1106-preview",
            )
            id = openai_assistant.id
        else:
            id = agent._openai_assistant.id
        function_models = [GetFunctionModel(auth=sender.auth, name=function_name) for function_name in functions_to_add]
        functions = FunctionsService.get_functions(function_models)

        # Create a set of function names for easy lookup
        retrieved_function_names = {func.name for func in functions if func}

        # Check if all functions are retrieved
        for function_to_add in functions_to_add:
            if function_to_add not in retrieved_function_names:
                if created_assistant:
                    sender.openai_client.beta.assistants.delete(assistant_id=id)
                return json.dumps({"error": f"Function({function_to_add}) not found"})

        agent, err = AgentService.upsert_agents([UpsertAgentModel(
            auth=sender.auth,
            name=name,
            description=description,
            system_message=custom_instructions,
            functions_to_add=functions_to_add,
            functions_to_remove=functions_to_remove,
            category=category,
            capability=capability,
            assistant_id=id
        )])
        if err is not None:
            if created_assistant:
                sender.openai_client.beta.assistants.delete(assistant_id=id)
            return err
        return json.dumps({"response": f"Agent({name}) upserted!"})

    @staticmethod
    def upload_file(sender: GPTAssistantAgent, description: str, data_or_url: str) -> str:
        from . import UpsertAgentModel
        if sender is None:
            return json.dumps({"error": "Sender not found"})

        # Step 1: Download the file if `data_or_url` is a URL
        if data_or_url.startswith('http://') or data_or_url.startswith('https://'):
            response = requests.get(data_or_url)
            if response.status_code != 200:
                return json.dumps({"error": f"Failed to download the file from URL: {data_or_url}"})
            file_data = response.content
        else:
            file_data = data_or_url

        # Step 2: Upload the file to OpenAI
        response = sender.openai_client.files.upload(file=file_data, purpose='assistants')
        if 'id' not in response:
            return json.dumps({"error": "Failed to upload the file to OpenAI"})

        file_id = response['id']

        # Step 3: Update the agent's record to include the new file_id
        agent, err = AgentService.upsert_agents([UpsertAgentModel(
            auth=sender.auth,
            name=sender.name,
            files_to_add={file_id: description}
        )])
        if err is not None:
            return err
        return json.dumps({"response": "File uploaded and agent updated successfully!"})

    @staticmethod
    def delete_files(sender: GPTAssistantAgent, file_ids: List[str]) -> str:
        from . import UpsertAgentModel
        if sender is None:
            return json.dumps({"error": "Sender not found"})

        # Step 1: Delete each file using OpenAI File API
        errors = []
        for file_id in file_ids:
            try:
                response = sender.openai_client.files.delete(file_id)
                if 'error' in response:
                    errors.append(f"Failed to delete file {file_id}: {response['error']}")
            except Exception as e:
                errors.append(f"Exception occurred while deleting file {file_id}: {str(e)}")

        if errors:
            return json.dumps({"error": "Some or all files failed to delete.", "details": errors})

        # Step 2: Update the agent's record to remove the file_ids
        try:
            agent, err = AgentService.upsert_agents([UpsertAgentModel(
                auth=sender.auth,
                name=sender.name,
                files_to_remove=file_ids
            )])
            if err is not None:
                return err
        except Exception as e:
            return json.dumps({"error": f"Failed to update the agent after file deletion: {str(e)}"})

        return json.dumps({"response": "Files deleted and agent updated successfully!"})

    @staticmethod
    def get_file_content(sender: GPTAssistantAgent, file_id: str) -> str:
        if sender is None:
            return json.dumps({"error": "Sender not found"})

        try:
            # Use the OpenAI client to retrieve the file content directly
            api_response = sender.openai_client.files.with_raw_response.retrieve_content(file_id)
            
            # Check if the request was successful
            if api_response.status_code == 200:
                content = api_response.content.decode('utf-8')  # Assuming the content is text
                return json.dumps({"response": content})
            else:
                return json.dumps({"error": f"Failed to retrieve file content, status code: {api_response.status_code}"})
        except Exception as e:
            return json.dumps({"error": f"Failed to retrieve file content: {str(e)}"})

    @staticmethod
    def _update_capability(agent):
        from . import FunctionsService, MakeService, INFO, MANAGEMENT, FILES, CODE_INTERPRETER, RETRIEVAL
        agent.llm_config["tools"] = []
        if agent.capability & INFO:
            for func_spec in group_info_function_specs:
                function_model, error_message = FunctionsService._create_function_model(agent, func_spec)
                if error_message:
                    return error_message
                FunctionsService.define_function_internal(agent, function_model) 
        if agent.capability & CODE_INTERPRETER:
            agent.llm_config["tools"].append({"type": "code_interpreter"})
        if agent.capability & RETRIEVAL:
            agent.llm_config["tools"].append({"type": "retrieval"})
        if agent.capability & FILES:
            for func_spec in files_function_specs:
                function_model, error_message = FunctionsService._create_function_model(agent, func_spec)
                if error_message:
                    return error_message
                FunctionsService.define_function_internal(agent, function_model)  
        if agent.capability & MANAGEMENT:
            for func_spec in management_function_specs:
                function_model, error_message = FunctionsService._create_function_model(agent, func_spec)
                if error_message:
                    return error_message
                FunctionsService.define_function_internal(agent, function_model)
        MakeService.AGENT_REGISTRY[agent.name] = agent

    @staticmethod
    def _create_agent(backend_agent) -> GPTAssistantAgent:
        llm_config = {"api_key": backend_agent.auth.api_key, "assistant_id": backend_agent.assistant_id}
        agent = GPTAssistantAgent(
                name=backend_agent.name,
                human_input_mode=backend_agent.human_input_mode,
                default_auto_reply=backend_agent.default_auto_reply,
                instructions=backend_agent.system_message,
                is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
                llm_config=llm_config
            )
        agent.auth = backend_agent.auth
        return agent

    @staticmethod
    def update_agent(agent, backend_agent):
        from . import FunctionsService, AddFunctionModel, GetFunctionModel
        agent.update_system_message(backend_agent.system_message)
        agent.description = backend_agent.description
        agent.capability = backend_agent.capability
        agent.files = backend_agent.files
        agent.function_names = backend_agent.function_names
        AgentService._update_capability(agent)
        if backend_agent.function_names:
            function_models = [GetFunctionModel(auth=agent.auth, name=function_name) for function_name in backend_agent.function_names]
            functions = FunctionsService.get_functions(function_models)

            # Create a set of function names for easy lookup
            retrieved_function_names = {func.name for func in functions if func}

            # Check if all functions are retrieved
            for function_name in backend_agent.function_names:
                if function_name not in retrieved_function_names:
                    return json.dumps({"error": f"Function({function_name}) not found"})

            for function in functions:
                FunctionsService.define_function_internal(agent, AddFunctionModel(**function.dict(), auth=agent.auth))
        agent._openai_assistant = agent.openai_client.beta.assistants.update(
            assistant_id=agent.llm_config.get("assistant_id", None),
            instructions=agent.system_message,
            description=agent.description,
            tools=agent.llm_config.get("tools", []),
            file_ids=list(backend_agent.files.keys())
        )
        return None

    @staticmethod
    def make_agent(backend_agent):
        from . import FunctionsService, AddFunctionModel, GetFunctionModel
        agent = AgentService._create_agent(backend_agent)
        if agent is None:
            return None, json.dumps({"error": "Could not make agent"})
        agent.description = backend_agent.description
        agent.custom_instructions = agent.system_message
        agent.capability = backend_agent.capability
        agent.files = backend_agent.files
        agent.function_names = backend_agent.function_names
        AgentService._update_capability(agent)
        if backend_agent.function_names:
            function_models = [GetFunctionModel(auth=agent.auth, name=function_name) for function_name in backend_agent.function_names]
            functions = FunctionsService.get_functions(function_models)

            # Create a set of function names for easy lookup
            retrieved_function_names = {func.name for func in functions if func}

            # Check if all functions are retrieved
            for function_name in backend_agent.function_names:
                if function_name not in retrieved_function_names:
                    return json.dumps({"error": f"Function({function_name}) not found"})

            for function in functions:
                FunctionsService.define_function_internal(agent, AddFunctionModel(**function.dict(), auth=agent.auth))
        agent._openai_assistant = agent.openai_client.beta.assistants.update(
            assistant_id=agent.llm_config.get("assistant_id", None),
            instructions=agent.system_message,
            description=agent.description,
            tools=agent.llm_config.get("tools", []),
            file_ids=list(backend_agent.files.keys())
        )
        return agent, None

    @staticmethod
    def upsert_agents(upsert_models):
        from . import BackendService, GetAgentModel, MakeService
        # Step 1: Upsert all agents in batch
        err = BackendService.upsert_backend_agents(upsert_models)
        if err and err != json.dumps({"error": "No agents were upserted, no changes found!"}):
            return None, err

        # Step 2: Retrieve all agents from backend in batch
        get_agent_models = [GetAgentModel(auth=model.auth, name=model.name) for model in upsert_models]
        backend_agents, err = BackendService.get_backend_agents(get_agent_models)
        if err:
            return None, err
        if len(backend_agents) == 0:
            return None, json.dumps({"error": "Could not fetch agents from backend"})

        # Step 3: Update local agent registry
        successful_agents = []
        for backend_agent in backend_agents:
            agent = MakeService.AGENT_REGISTRY.get(backend_agent.name)
            if agent is None:
                agent, err = AgentService.make_agent(backend_agent)
                if err is not None:
                    return None, err
            else:
                err = AgentService.update_agent(agent, backend_agent)
                if err is not None:
                    return None, err
            successful_agents.append(agent)
        return successful_agents, None

    @staticmethod
    def _generate_group_stats_text(group_manager: GroupChatManager) -> str:
        incoming_communications = "\n".join(
            f"- Group: {agent_name}: {count} message(s)"
            for agent_name, count in group_manager.incoming.items()
        )
        outgoing_communications = "\n".join(
            f"- Group: {agent_name}: {count} message(s)"
            for agent_name, count in group_manager.outgoing.items()
        )
        communications = f"Incoming communications:\n{incoming_communications}\nOutgoing communications:\n{outgoing_communications}"
        if group_manager.dependent:
            communications = f"{communications}\nCurrent Dependent Group:\n{group_manager.dependent.name}"
        return communications.strip()


    @staticmethod
    def get_capability_names(capability_number):
        from . import INFO, CODE_INTERPRETER, RETRIEVAL, FILES, MANAGEMENT
        capabilities = [
            ("INFO", INFO),
            ("CODE_INTERPRETER", CODE_INTERPRETER),
            ("RETRIEVAL", RETRIEVAL),
            ("FILES", FILES),
            ("MANAGEMENT", MANAGEMENT),
        ]
        capability_names = [name for name, bit in capabilities if capability_number & bit]
        return capability_names

    @staticmethod
    def update_agent_system_message(agent: GPTAssistantAgent, group_manager: GroupChatManager) -> None:
        from . import MakeService, MANAGEMENT
        capability_names = AgentService.get_capability_names(agent.capability)
        capability_text = ", ".join(capability_names) if capability_names else "No capabilities"
        formatted_message = ""
        dependent = f', dependent group: {group_manager.dependent.name}' if group_manager.dependent else ''
        # Update the system message based on the agent type
        if agent.capability & MANAGEMENT:
            # Define the new agent system message with placeholders filled in
            formatted_message = AgentService.MANAGER_AGENT_SYSTEM_MESSAGE.format(
                agent_name=agent.name,
                agent_description=MakeService._get_short_description(agent.description),
                group_name=group_manager.name,
                custom_instructions=agent.custom_instructions,
                dependent=dependent,
                capability_instruction=AgentService.CAPABILITY_SYSTEM_MESSAGE,
                capabilities=capability_text,
                group_stats=AgentService._generate_group_stats_text(group_manager),
            )
        else:
            # Define the new agent system message with placeholders filled in
            formatted_message = AgentService.BASIC_AGENT_SYSTEM_MESSAGE.format(
                agent_name=agent.name,
                agent_description=MakeService._get_short_description(agent.description),
                group_name=group_manager.name,
                custom_instructions=agent.custom_instructions,
                dependent=dependent,
                capability_instruction=AgentService.CAPABILITY_SYSTEM_MESSAGE,
                capabilities=capability_text
            )
        agent.update_system_message(formatted_message)
