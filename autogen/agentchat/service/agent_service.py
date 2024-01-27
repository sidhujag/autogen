from .. import GroupChatManager
from ..contrib.gpt_assistant_agent import GPTAssistantAgent
from typing import List
from autogen.agentchat.service.function_specs import management_function_specs, get_function_info_spec, group_info_function_specs, files_function_specs
import json
import requests

class AgentService:
    BASIC_AGENT_SYSTEM_MESSAGE: str = """
Agent Details: Name: {agent_name}, Description: {agent_description}, Group: {group_name}, {capability_instruction}

Review the functions you have been given carefully, especially the parameters. Use them effectively. If you are unsure about the parameters you can use get_function_info which will return the function spec.

You work in an agent framework, comprised of functions (tools) within agents which are within groups. Groups can be nested and hiearchical.

As a Basic Agent, your role is to collaborate effectively with your peers, utilizing your unique skills to achieve common goals. When faced with complex tasks, plan meticulously, assigning roles to suitable agents or groups. Functions are used within agents which are used withing groups. You can tag the manager in your group through text-interaction to have agents/groups modified or to start nested chats with other groups. Strive for comprehensive and creative solutions, focusing on the task at hand. Prioritize reusing existing functions, agents, and groups. If a specific function is requested, first check its availability. If it's not available, communicate this clearly and suggest alternatives. Be cautious with non-accepted functions; if you do choose them then repair them rather than creating new versions. Prefer to use accepted functions over non-accepted. Always consider the group's message history in your responses.

Ensure to review the group's message history thoroughly before initiating a redundant action. Additionally, if the context indicates that a request has been previously addressed, you will acknowledge and proceed from the most recent state of information.

Read each function you have been give carefully to discover and enhance your abilities.

If you have termination access, don't terminate if a path doesn't work out right away, exhaust all of your possibilities to try different things to try to solve the problem. Terminate groups judiciously based on the conversation's progress and relevance, avoiding circular discussions or repeated statements.

Locked groups are good at specific jobs. Unlocked groups are good for abstract or further assignment of roles/tasks downstream.

For coding always use the relevant software group.

You send messages to other agents via your responses, for example agent messaging bob: @bob: can you tell me about point number 4? The group chat manager auto-select's the next speaker in the group based on your text-based responses.

I have been provided with the capability to review the group's message history, and it's my responsibility to ensure that I do not initiate redundant actions. In this instance, I should have noted that the unit tests for the `create_food` function had already been addressed and should not have been requested again. 

You will make sure to cross-reference the context and the outcomes of previous actions before proceeding with any new ones. You must avoid redundancy by only making necessary and unique requests. This will prevent unnecessary repetitions and align with the goal of efficient and coherent task management.

CHECK YOUR CONTEXT BEFORE RE-REQUESTING INFORMATION FROM FUNCTIONS YOU ALREADY HAVE CALLED.

Custom Instructions: {custom_instructions}

Group Stats: {group_stats}
"""

    MANAGER_AGENT_SYSTEM_MESSAGE: str = """
Agent Details: Name: {agent_name}, Description: {agent_description}, Group: {group_name}, {capability_instruction}

Review the functions you have been given carefully, especially the parameters. Use them effectively. If you are unsure about the parameters you can use get_function_info which will return the function spec.

You work in an agent framework, comprised of functions (tools) within agents which are within groups. Groups can be nested and hiearchical.

As a Manager Agent, you are tasked with leading and coordinating group activities. Develop comprehensive strategies, assign tasks effectively, and utilize your management tools for optimal problem-solving. Encourage focus and creativity within your team. Functions are used within agents which are used withing groups. When a specific function is requested, first attempt to access or add it. If this is not possible, provide a clear explanation and suggest viable alternatives. Avoid creating new entities if existing ones are adequate. Be wary of non-accepted functions and aim to improve them if you do choose them. Prefer to use accepted functions over non-accepted. Ensure your responses reflect the group's message history. Managers can send other groups messages which run as nested chats returning responses as summaries.

Ensure to review the group's message history thoroughly before initiating a redundant action. Additionally, if the context indicates that a request has been previously addressed, you will acknowledge and proceed from the most recent state of information.

Watch for others tagging you in the chat for certain requests like modifying agents and groups only you can fulfill.

Read each function you have been give carefully to discover and enhance your abilities.

If you have termination access, don't terminate if a path doesn't work out right away, exhaust all of your possibilities to try different things to try to solve the problem. Terminate groups judiciously based on the conversation's progress and relevance, avoiding circular discussions or repeated statements.

Locked groups are good at specific jobs. Unlocked groups are good for abstract or further assignment of roles/tasks downstream.

For coding always use the relevant software group.

You send messages to other agents via your responses, for example agent messaging bob: @bob: can you tell me about point number 4? The group chat manager auto-select's the next speaker in the group based on your text-based responses.

You will make sure to cross-reference the context and the outcomes of previous actions before proceeding with any new ones. You must avoid redundancy by only making necessary and unique requests. This will prevent unnecessary repetitions and align with the goal of efficient and coherent task management.

CHECK YOUR CONTEXT BEFORE RE-REQUESTING INFORMATION FROM FUNCTIONS YOU ALREADY HAVE CALLED.

Custom Instructions: {custom_instructions}

Group Stats: {group_stats}
"""

    # Define capability instruction variables
    DISCOVERY_INSTRUCTIONS = "Access and manage information on functions, agents, and groups. Discover entities and gather relevant data."
    TERMINATE_INSTRUCTIONS = "Ability to terminate a group, concluding its operations by replying with just 'TERMINATE'."
    OPENAI_CODE_INTERPRETER_INSTRUCTIONS = "Create and executes simple code through natural language using the OpenAI Code Interpreter and provides response in interactions. Ideal for isolated, internet-independent tasks."
    OPENAI_RETRIEVAL_INSTRUCTIONS = "Leverage OpenAI's capabilities to enhance knowledge retrieval, utilizing external documents and data."
    OPENAI_FILES_INSTRUCTIONS = "Manage and utilize OpenAI Files for data processing, sharing, and state management across OpenAI Code Interpreter and Retrieval tools."
    MANAGEMENT_INSTRUCTIONS = "Oversee and modify agents/groups, facilitate inter-group communication, and manage overall group activities."

    @staticmethod
    async def get_agent(agent_model) -> GPTAssistantAgent:
        from . import BackendService, MakeService, DeleteAgentModel
        agent: GPTAssistantAgent = MakeService.AGENT_REGISTRY.get(agent_model.name)
        if agent is None:
            backend_agents, err = await BackendService.get_backend_agents([agent_model])
            if err is None and len(backend_agents) > 0:
                agent, err = await AgentService.make_agent(backend_agents[0])
                if err is None and agent:
                    MakeService.AGENT_REGISTRY[agent_model.name] = agent
                else:
                    await BackendService.delete_backend_agents([DeleteAgentModel(name=agent_model.name)])
        return agent

    @staticmethod
    async def discover_agents(query: str, category: str = None) -> str:
        from . import BackendService, DiscoverAgentsModel
        response, err = await BackendService.discover_backend_agents(DiscoverAgentsModel(query=query,category=category))
        if err is not None:
            return err
        return response

    @staticmethod
    async def get_agent_info(name: str) -> str:
        from . import GetAgentModel, AgentService, MakeService, FunctionsService, GetFunctionModel, AgentInfo, FunctionInfo
        agent = await AgentService.get_agent(GetAgentModel(name=name))
        if agent is None:
            return json.dumps({"error": f"Agent({name}) not found"})

        function_models = [GetFunctionModel(name=function_name) for function_name in agent.function_names]
        functions = await FunctionsService.get_functions(function_models)

        # Convert BaseFunction objects to FunctionInfo objects
        function_info_list = [FunctionInfo(name=func.name, status=func.status) for func in functions]

        agentInfo = AgentInfo(
            name=agent.name,
            description=MakeService._get_short_description(agent.description),
            system_message=MakeService._get_short_description(agent.system_message),
            capability=agent.capability,
            files=agent.files,
            functions=function_info_list
        )
        return json.dumps({"response": agentInfo.dict()})

    
    @staticmethod
    async def upsert_agent(agent: str, description: str = None, custom_instructions: str = None, functions_to_add: List[str] = None,  functions_to_remove: List[str] = None, category: str = None, capability: int = 1) -> str: 
        from . import UpsertAgentModel, GetAgentModel, FunctionsService, GetFunctionModel, MakeService
        agent_obj = await AgentService.get_agent(GetAgentModel(name=agent))
        id = None
        created_assistant = False
        if agent_obj is None:
            created_assistant = True
            # place holder to get assistant id
            openai_assistant = MakeService.openai_client.beta.assistants.create(
                name=agent,
                instructions="",
                tools=[],
                model="gpt-4-turbo-preview",
            )
            id = openai_assistant.id
        else:
            id = agent_obj._openai_assistant.id
        function_models = [GetFunctionModel(name=function_name) for function_name in functions_to_add]
        functions = await FunctionsService.get_functions(function_models)
        if not functions and functions_to_add:
            return json.dumps({"error": "Functions you are trying to add are not found"})
        # Create a set of function names for easy lookup
        retrieved_function_names = {func.name for func in functions if func}
        # Check if all functions are retrieved
        for function_to_add in functions_to_add:
            if function_to_add not in retrieved_function_names:
                if created_assistant:
                    MakeService.openai_client.beta.assistants.delete(assistant_id=id)
                return json.dumps({"error": f"Function({function_to_add}) not found"})
        agent_obj, err = await AgentService.upsert_agents([UpsertAgentModel(
            name=agent,
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
                MakeService.openai_client.beta.assistants.delete(assistant_id=id)
            return err
        return json.dumps({"response": f"Agent({agent}) upserted!"})

    @staticmethod
    async def upload_file(agent: str, description: str, data_or_url: str) -> str:
        from . import UpsertAgentModel, MakeService

        # Step 1: Download the file if `data_or_url` is a URL
        if data_or_url.startswith('http://') or data_or_url.startswith('https://'):
            response = requests.get(data_or_url)
            if response.status_code != 200:
                return json.dumps({"error": f"Failed to download the file from URL: {data_or_url}"})
            file_data = response.content
        else:
            file_data = data_or_url

        # Step 2: Upload the file to OpenAI
        response = MakeService.openai_client.files.upload(file=file_data, purpose='assistants')
        if 'id' not in response:
            return json.dumps({"error": "Failed to upload the file to OpenAI"})

        file_id = response['id']

        # Step 3: Update the agent's record to include the new file_id
        agent_obj, err = await AgentService.upsert_agents([UpsertAgentModel(
            name=agent,
            files_to_add={file_id: description}
        )])
        if err is not None:
            return err
        return json.dumps({"response": "File uploaded and agent updated successfully!"})

    @staticmethod
    async def delete_files(agent: str, file_ids: List[str]) -> str:
        from . import UpsertAgentModel, MakeService
        # Step 1: Delete each file using OpenAI File API
        errors = []
        for file_id in file_ids:
            try:
                response = MakeService.openai_client.files.delete(file_id)
                if 'error' in response:
                    errors.append(f"Failed to delete file {file_id}: {response['error']}")
            except Exception as e:
                errors.append(f"Exception occurred while deleting file {file_id}: {str(e)}")

        if errors:
            return json.dumps({"error": "Some or all files failed to delete.", "details": errors})

        # Step 2: Update the agent's record to remove the file_ids
        try:
            agent, err = await AgentService.upsert_agents([UpsertAgentModel(
                name=agent,
                files_to_remove=file_ids
            )])
            if err is not None:
                return err
        except Exception as e:
            return json.dumps({"error": f"Failed to update the agent after file deletion: {str(e)}"})

        return json.dumps({"response": "Files deleted and agent updated successfully!"})

    @staticmethod
    def get_file_content(file_id: str) -> str:
        from . import MakeService
        try:
            # Use the OpenAI client to retrieve the file content directly
            api_response = MakeService.openai_client.files.with_raw_response.retrieve_content(file_id)
            
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
        from . import FunctionsService, MakeService, DISCOVERY, TERMINATE, OPENAI_RETRIEVAL, MANAGEMENT, OPENAI_FILES, OPENAI_CODE_INTERPRETER
        agent.llm_config["tools"] = []
        agent._code_execution_config = {}
        function_model, error_message = FunctionsService._create_function_model(get_function_info_spec)
        if error_message:
            return error_message
        FunctionsService.define_function_internal(agent, function_model)
        if agent.capability & DISCOVERY:
            for func_spec in group_info_function_specs:
                function_model, error_message = FunctionsService._create_function_model(func_spec)
                if error_message:
                    return error_message
                FunctionsService.define_function_internal(agent, function_model) 
        if agent.capability & TERMINATE:
           agent._is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("TERMINATE.")
        if agent.capability & OPENAI_CODE_INTERPRETER:
            agent.llm_config["tools"].append({"type": "code_interpreter"})
        if agent.capability & OPENAI_RETRIEVAL:
            agent.llm_config["tools"].append({"type": "retrieval"})
        if agent.capability & OPENAI_FILES:
            for func_spec in files_function_specs:
                function_model, error_message = FunctionsService._create_function_model(func_spec)
                if error_message:
                    return error_message
                FunctionsService.define_function_internal(agent, function_model)
        if agent.capability & MANAGEMENT:
            for func_spec in management_function_specs:
                function_model, error_message = FunctionsService._create_function_model(func_spec)
                if error_message:
                    return error_message
                FunctionsService.define_function_internal(agent, function_model)
        MakeService.AGENT_REGISTRY[agent.name] = agent

    @staticmethod
    def _create_agent(backend_agent) -> GPTAssistantAgent:
        from . import MakeService
        llm_config = {"api_key": MakeService.auth.api_key, "assistant_id": backend_agent.assistant_id}
        agent = GPTAssistantAgent(
                name=backend_agent.name,
                default_auto_reply=backend_agent.default_auto_reply,
                instructions=backend_agent.system_message,
                is_termination_msg=lambda x: False,
                llm_config=llm_config,
                human_input_mode=backend_agent.human_input_mode,
            )
        return agent

    @staticmethod
    async def update_agent(agent, backend_agent):
        from . import FunctionsService, GetFunctionModel, MakeService
        agent.update_system_message(backend_agent.system_message)
        agent.description = backend_agent.description
        agent.capability = backend_agent.capability
        agent.files = backend_agent.files
        agent.function_names = backend_agent.function_names
        AgentService._update_capability(agent)
        if backend_agent.function_names:
            function_models = [GetFunctionModel(name=function_name) for function_name in backend_agent.function_names]
            functions = await FunctionsService.get_functions(function_models)

            # Create a set of function names for easy lookup
            retrieved_function_names = {func.name for func in functions if func}
            # Check if all functions are retrieved
            for function_name in backend_agent.function_names:
                if function_name not in retrieved_function_names:
                    return json.dumps({"error": f"Function({function_name}) not found"})

            for function in functions:
                FunctionsService.define_function_internal(agent, function)
        agent._openai_assistant = MakeService.openai_client.beta.assistants.update(
            assistant_id=backend_agent.assistant_id,
            instructions=agent.system_message,
            description=agent.description,
            tools=agent.llm_config.get("tools", []),
            file_ids=list(backend_agent.files.keys())
        )
        return None

    @staticmethod
    async def make_agent(backend_agent):
        from . import FunctionsService, GetFunctionModel, MakeService
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
            function_models = [GetFunctionModel(name=function_name) for function_name in backend_agent.function_names]
            functions = await FunctionsService.get_functions(function_models)
            # Create a set of function names for easy lookup
            retrieved_function_names = {func.name for func in functions if func}
            # Check if all functions are retrieved
            for function_name in backend_agent.function_names:
                if function_name not in retrieved_function_names:
                    return None, json.dumps({"error": f"Function({function_name}) not found"})

            for function in functions:
                FunctionsService.define_function_internal(agent, function)
        agent._openai_assistant = MakeService.openai_client.beta.assistants.update(
            assistant_id=backend_agent.assistant_id,
            instructions=agent.system_message,
            description=agent.description,
            tools=agent.llm_config.get("tools", []),
            file_ids=list(backend_agent.files.keys())
        )
        return agent, None

    @staticmethod
    async def upsert_agents(upsert_models):
        from . import BackendService, GetAgentModel, MakeService, DeleteAgentModel
        # Step 1: Upsert all agents in batch
        err = await BackendService.upsert_backend_agents(upsert_models)
        if err and err != json.dumps({"error": "No agents were upserted, no changes found!"}):
            return None, err

        # Step 2: Retrieve all agents from backend in batch
        get_agent_models = [GetAgentModel(name=model.name) for model in upsert_models]
        backend_agents, err = await BackendService.get_backend_agents(get_agent_models)
        if err:
            return None, err
        if len(backend_agents) == 0:
            return None, json.dumps({"error": "Could not fetch agents from backend"})

        # Step 3: Update local agent registry
        successful_agents = []
        for backend_agent in backend_agents:
            agent = MakeService.AGENT_REGISTRY.get(backend_agent.name)
            if agent is None:
                agent, err = await AgentService.make_agent(backend_agent)
                if err is not None:
                    await BackendService.delete_backend_agents([DeleteAgentModel(name=backend_agent.name)])
                    return None, err
            else:
                err = await AgentService.update_agent(agent, backend_agent)
                if err is not None:
                    return None, err
            successful_agents.append(agent)
        return successful_agents, None

    @staticmethod
    def _generate_group_stats_text(group_manager: GroupChatManager) -> str:
        # Recursive function to get parent group information
        def get_parent_group_info(manager, indent_level=0):
            if manager.parent_group is None:
                return ""
            indent = "    " * indent_level
            parent_info = f"{indent}- Parent Group: {manager.parent_group.name}\n"
            return parent_info + get_parent_group_info(manager.parent_group, indent_level + 1)

        incoming_communications = "\n".join(
            f"- Group: {agent_name}: {count} message(s)"
            for agent_name, count in group_manager.incoming.items()
        )
        outgoing_communications = "\n".join(
            f"- Group: {agent_name}: {count} message(s)"
            for agent_name, count in group_manager.outgoing.items()
        )

        parent_group_info = get_parent_group_info(group_manager)
        communications = f"\n\nIncoming communications:\n{incoming_communications}\nOutgoing communications:\n{outgoing_communications}"

        if group_manager.current_code_assistant_name:
            communications += f"\n\nCurrent code assistant:\n{group_manager.current_code_assistant_name}"

        if parent_group_info:
            communications = f"\n\nParent Group Information:\n{parent_group_info}\n" + communications

        return communications.strip()


    @staticmethod
    def get_capability_instructions(capability_number) -> str:
        # Define a list of capabilities, each with name, bit, and instructions
        capabilities = [
            ("DISCOVERY", 1, AgentService.DISCOVERY_INSTRUCTIONS),
            ("TERMINATE", 2, AgentService.TERMINATE_INSTRUCTIONS),
            ("OPENAI_CODE_INTERPRETER", 4, AgentService.OPENAI_CODE_INTERPRETER_INSTRUCTIONS),
            ("OPENAI_RETRIEVAL", 8, AgentService.OPENAI_RETRIEVAL_INSTRUCTIONS),
            ("OPENAI_FILES", 16, AgentService.OPENAI_FILES_INSTRUCTIONS),
            ("MANAGEMENT", 32, AgentService.MANAGEMENT_INSTRUCTIONS),
        ]

        # Extract instructions for each enabled capability
        capability_instructions = []
        for name, bit, instr in capabilities:
            if capability_number & bit:
                capability_instructions.append(f"{name} ({bit}): {instr}")
        if not capability_instructions:
            capability_instructions.append("No capabilities")
        capability_instructions_str = "\n".join(capability_instructions)
        return f"Agent Capability Breakdown:\n{capability_instructions_str}"

    @staticmethod
    def update_agent_system_message(agent: GPTAssistantAgent, group_manager: GroupChatManager) -> None:
        from . import MakeService, MANAGEMENT
        formatted_message = ""
        # Get capability instructions
        capability_instructions_instr = AgentService.get_capability_instructions(agent.capability)

        # Update the system message based on the agent type
        if agent.capability & MANAGEMENT:
            # Define the new agent system message with placeholders filled in
            formatted_message = AgentService.MANAGER_AGENT_SYSTEM_MESSAGE.format(
                agent_name=agent.name,
                agent_description=MakeService._get_short_description(agent.description),
                group_name=group_manager.name,
                custom_instructions=agent.custom_instructions,
                capability_instruction=capability_instructions_instr,
                group_stats=AgentService._generate_group_stats_text(group_manager),
            )
        else:
            # Define the new agent system message with placeholders filled in
            formatted_message = AgentService.BASIC_AGENT_SYSTEM_MESSAGE.format(
                agent_name=agent.name,
                agent_description=MakeService._get_short_description(agent.description),
                group_name=group_manager.name,
                custom_instructions=agent.custom_instructions,
                capability_instruction=capability_instructions_instr,
                group_stats=AgentService._generate_group_stats_text(group_manager),
            )
        agent.update_system_message(formatted_message)
