from .. import GroupChatManager
from ..contrib.gpt_assistant_agent import GPTAssistantAgent
from typing import List, Optional, Union
from autogen import OpenAIWrapper
from autogen.agentchat.service.function_specs import management_function_specs, group_info_function_specs, files_function_specs
import json

class AgentService:
    BASIC_AGENT_SYSTEM_MESSAGE: str = """Agent, you are a cog in a complex AI hierarchy, designed to solve tasks collaboratively. Solve tasks step-by-step.

Agent name and Group: Your name: {agent_name}, description: {agent_description}, group: {group_name}, capabilities: {capabilities}

{capability_instruction}

You are announcing messages to a group. You are not talking directly to agents but can refer to them or talk to them via chat interaction.

Stay on topic and don't deviate away from the main task for the group. If you have nothing to say just say you have nothing to add. Try all possibilities to solve your task but deviate away from topic.

As a basic agent you will follow the custom instructions and any functions you have to complete your given task, with the help of your peers in your group as needed.

Custom instructions: {custom_instructions}
"""
    MANAGER_AGENT_SYSTEM_MESSAGE: str = """Agent, you are a cog in a complex AI hierarchy, designed to solve tasks collaboratively. Solve tasks step-by-step. 
    
Agent name and Group: Your name: {agent_name}, description: {agent_description}, group: {group_name}, capabilities: {capabilities}

{capability_instruction}

Carefully read the functions provided to you as well as your capabilities above to learn of your abilities and responsibilities. All instructions are presented through the functions.

Termination should be decided at your discretion. Read the room. If agents have nothing to add, if the conversation reaches a natural conclusion or if the discussion topic switches, it may be time to terminate.

You are general purpose and aware of other agents' surroundings as well as yours. You will manage yourself as well as your BASIC peers.

You are announcing messages to a group. You are not talking directly to agents but can refer to them or talk to them via chat interaction.

Keep agents on topic and don't deviate away from the reason your group exists. Ensure your peers do not give up without exhausting all possibilities through the help of MANAGEMENT agents such as yourself as well as their own abilities.

Custom instructions: {custom_instructions}

GROUP STATS
{group_stats}
"""
    CAPABILITY_SYSTEM_MESSAGE: str = """Agent Capability Breakdown:
    - GROUP_INFO: Able to get group information (list group agents, list group files, stats) on demand via get_group_info function.
    - CODE_INTERPRETER_TOOL: Allows the agent to write and run Python code in a sandboxed environment. Interpreter can natively work with files for advanced coding usecases.
    - RETRIEVAL_TOOL: Expands the agent's knowledge base with external documents and data. Uses files to create knowledge base.
    - FILES: Provides the ability to manage files for data processing and sharing across groups.
    - MANAGEMENT: Grants the agent the power to modify agents/functions/groups, communicate with other groups, discover entities, and manage group activities (including termination).
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
    def upsert_agent(sender: GPTAssistantAgent, name: str, description: str = None, system_message: str = None, functions_to_add: List[str] = None,  functions_to_remove: List[str] = None, category: str = None, capability: int = 1) -> str: 
        from . import UpsertAgentModel, GROUP_INFO
        if sender is None:
            return json.dumps({"error": "Sender not found"})
        if not capability & GROUP_INFO:
            return json.dumps({"error": "GROUP_INFO bit must be set for capability"})
        agent, err = AgentService.upsert_agents([UpsertAgentModel(
            auth=sender.auth,
            name=name,
            description=description,
            system_message=system_message,
            functions_to_add=functions_to_add,
            functions_to_remove=functions_to_remove,
            category=category,
            capability=capability
        )])
        if err is not None:
            return err
        return json.dumps({"response": "Agent upserted!"})

    @staticmethod
    def _update_capability(agent):
        from . import FunctionsService, MakeService, GROUP_INFO, MANAGEMENT, FILES, CODE_INTERPRETER_TOOL, RETRIEVAL_TOOL
        agent.llm_config["tools"] = []
        if agent.capability & GROUP_INFO:
            for func_spec in group_info_function_specs:
                function_model, error_message = FunctionsService._create_function_model(agent, func_spec)
                if error_message:
                    return error_message
                FunctionsService.define_function_internal(agent, function_model) 
        if agent.capability & CODE_INTERPRETER_TOOL:
            agent.llm_config["tools"].append({"type": "code_interpreter"})
        if agent.capability & RETRIEVAL_TOOL:
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
    def _create_agent(backend_agent, llm_config: Optional[Union[dict, bool]] = None) -> GPTAssistantAgent:
        config = {"api_key": backend_agent.auth.api_key, "assistant_id": backend_agent.assistant_id}
        if llm_config:
            llm_config.update(config)
        else:
           llm_config = config
        agent = GPTAssistantAgent(
                name=backend_agent.name,
                human_input_mode=backend_agent.human_input_mode,
                default_auto_reply=backend_agent.default_auto_reply,
                instructions=backend_agent.system_message,
                llm_config=llm_config
            )
        agent.auth = backend_agent.auth
        return agent

    @staticmethod
    def update_agent(agent, backend_agent):
        from . import FunctionsService, AddFunctionModel
        agent.update_system_message(backend_agent.system_message)
        agent.description = backend_agent.description
        agent.capability = backend_agent.capability
        agent.llm_config["tools"] = AgentService._update_capability(agent)
        if len(backend_agent.functions) > 0:
            for function in backend_agent.functions:
                FunctionsService.define_function_internal(agent, AddFunctionModel(**function, auth=agent.auth))
        file_ids = []
        if len(backend_agent.files) > 0:
            file_ids = [file.file_id for file in backend_agent.files.values()]
        agent._openai_assistant = agent._openai_client.beta.assistants.update(
            assistant_id=agent.llm_config.get("assistant_id", None),
            instructions=agent.system_message,
            description=agent.description,
            tools=agent.llm_config.get("tools", []),
            file_ids=file_ids,
        )

    @staticmethod
    def make_agent(backend_agent, llm_config: Optional[Union[dict, bool]] = None):
        from . import FunctionsService, AddFunctionModel
        llm_config['assistant_id'] = backend_agent.assistant_id
        agent = AgentService._create_agent(backend_agent, llm_config)
        if agent is None:
            return None, json.dumps({"error": "Could not make agent"})
        agent.description = backend_agent.description
        agent.custom_system_message = agent.system_message
        agent.capability = backend_agent.capability
        AgentService._update_capability(agent)
        if len(backend_agent.functions) > 0:
            for function in backend_agent.functions:
                FunctionsService.define_function_internal(agent, AddFunctionModel(**function, auth=agent.auth))
        file_ids = []
        if len(backend_agent.files) > 0:
            file_ids = [file.file_id for file in backend_agent.files.values()]
        agent._openai_assistant = agent._openai_client.beta.assistants.update(
            assistant_id=agent.llm_config.get("assistant_id", None),
            instructions=agent.system_message,
            description=agent.description,
            tools=agent.llm_config.get("tools", []),
            file_ids=file_ids,
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
                AgentService.update_agent(agent, backend_agent)
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
        return communications.strip()


    @staticmethod
    def get_capability_names(capability_number):
        from . import GROUP_INFO, CODE_INTERPRETER_TOOL, RETRIEVAL_TOOL, FILES, MANAGEMENT
        capabilities = [
            ("GROUP_INFO", GROUP_INFO),
            ("CODE_INTERPRETER_TOOL", CODE_INTERPRETER_TOOL),
            ("RETRIEVAL_TOOL", RETRIEVAL_TOOL),
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
        formatted_message = None
        # Update the system message based on the agent type
        if agent.capability & MANAGEMENT:
            # Define the new agent system message with placeholders filled in
            formatted_message = AgentService.MANAGER_AGENT_SYSTEM_MESSAGE.format(
                agent_name=agent.name,
                agent_description=MakeService._get_short_description(agent.description),
                group_name=group_manager.name,
                custom_instructions=agent.custom_system_message,
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
                custom_instructions=agent.custom_system_message,
                capability_instruction=AgentService.CAPABILITY_SYSTEM_MESSAGE,
                capabilities=capability_text
            )
        agent._openai_assistant = agent._openai_client.beta.assistants.update(
            assistant_id=agent.assistant_id,
            instructions=formatted_message,
        )
