from .. import ConversableAgent, GroupChatManager
from typing import List, Optional, Union
from autogen import OpenAIWrapper
from autogen.agentchat.service.function_specs import function_specs
import json

class AgentService:
    BASIC_AGENT_SYSTEM_MESSAGE: str = """Agent, you are a cog in a complex AI hierarchy, designed to solve tasks collaboratively. Solve tasks step-by-step.

Agent name and Group: Your name: {agent_name}, description: {agent_description}, agent type: BASIC, group: {group_name}

You are announcing messages to a group. You are not talking directly to agents but can refer to them or talk to them via chat interaction.

Stay on topic and don't deviate away from the main task for the group. If you have nothing to say just say you have nothing to add. Try all possibilities to solve your task but deviate away from topic.

As a basic agent you will follow the custom instructions and any functions you have to complete your given task, with the help of your peers in your group as needed.

Custom instructions: {custom_instructions}
"""
    FULL_AGENT_SYSTEM_MESSAGE: str = """Agent, you are a cog in a complex AI hierarchy, designed to solve tasks collaboratively. Solve tasks step-by-step. 
    
Agent name and Group: Your name: {agent_name}, description: {agent_description}, agent type: FULL, group: {group_name}

You are general purpose and aware of other agents' surroundings as well as yours. You will manage yourself as well as your BASIC peers.

You are announcing messages to a group. You are not talking directly to agents but can refer to them or talk to them via chat interaction.

Keep agents on topic and don't deviate away from the reason your group exists. Ensure your peers do not give up without exhausting all possibilities through the help of FULL agents such as yourself as well as their own abilities.

Carefully read the functions provided to you to learn of your abilities and responsibilities. All instructions are presented through the functions.

Termination should be decided at your discretion. Read the room. If agents have nothing to add, if the conversation reaches a natural conclusion or if the discussion topic switches, it may be time to terminate.

Use the group stats as discovery for your currently "friended" groups. To discover your group peers use get_group_info.

Custom instructions: {custom_instructions}

GROUP STATS
{group_stats}
"""
    @staticmethod
    def get_agent(agent_model) -> ConversableAgent:
        from . import BackendService, MakeService
        agent: ConversableAgent = MakeService.AGENT_REGISTRY.get(agent_model.name)
        if agent is None:
            backend_agents, err = BackendService.get_backend_agents([agent_model])
            if err is None and len(backend_agents) > 0:
                agent, err = AgentService.make_agent(backend_agents[0])
                if err is not None:
                    MakeService.AGENT_REGISTRY[agent_model.name] = agent
        return agent

    @staticmethod
    def discover_agents(sender: ConversableAgent, query: str, category: str = None) -> str:
        from . import BackendService, DiscoverAgentsModel
        if sender is None:
            return json.dumps({"error": "Sender not found"})
        response, err = BackendService.discover_backend_agents(DiscoverAgentsModel(auth=sender.auth, query=query,category=category))
        if err is not None:
            return err
        return response

    @staticmethod
    def upsert_agent(sender: ConversableAgent, name: str, description: str = None, system_message: str = None, functions_to_add: List[str] = None,  functions_to_remove: List[str] = None, category: str = None, type: str = None) -> str: 
        from . import UpsertAgentModel
        if sender is None:
            return json.dumps({"error": "Sender not found"})
        agent, err = AgentService.upsert_agents([UpsertAgentModel(
            auth=sender.auth,
            name=name,
            description=description,
            system_message=system_message,
            functions_to_add=functions_to_add,
            functions_to_remove=functions_to_remove,
            category=category,
            type=type
        )])
        if err is not None:
            return err
        return json.dumps({"response": "Agent upserted!"})

    @staticmethod
    def _create_agent(backend_agent) -> ConversableAgent:
        from . import FunctionsService
        agent = ConversableAgent(
                name=backend_agent.name,
                human_input_mode=backend_agent.human_input_mode,
                default_auto_reply=backend_agent.default_auto_reply,
                system_message=backend_agent.system_message,
                llm_config={"api_key": backend_agent.auth.api_key}
            )
        agent.auth = backend_agent.auth
        if backend_agent.type == "FULL":
            # register the base functions for every FULL agent
            for func_spec in function_specs:
                function_model, error_message = FunctionsService._create_function_model(agent, func_spec)
                if error_message:
                    return error_message
                FunctionsService.define_function_internal(agent, function_model)
        return agent

    @staticmethod
    def update_agent(agent, backend_agent):
        from . import FunctionsService, AddFunctionModel, MakeService
        agent.update_system_message(backend_agent.system_message)
        agent.description = backend_agent.description
        if len(backend_agent.functions) > 0:
            for function in backend_agent.functions:
                FunctionsService.define_function_internal(agent, AddFunctionModel(**function, auth=agent.auth))
            agent.client = OpenAIWrapper(**agent.llm_config)
        MakeService.AGENT_REGISTRY[agent.name] = agent
    
    @staticmethod
    def make_agent(backend_agent, llm_config: Optional[Union[dict, bool]] = None):
        from . import FunctionsService, AddFunctionModel, MakeService
        agent = AgentService._create_agent(backend_agent)
        if agent is None:
            return None, json.dumps({"error": "Could not make agent"})
        agent.description = backend_agent.description
        agent.custom_system_message = agent.system_message
        agent.type = backend_agent.type
        if llm_config:
            agent.llm_config.update(llm_config)
        if len(backend_agent.functions) > 0:
            for function in backend_agent.functions:
                FunctionsService.define_function_internal(agent, AddFunctionModel(**function, auth=agent.auth))
        agent.client = OpenAIWrapper(**agent.llm_config)
        MakeService.AGENT_REGISTRY[agent.name] = agent
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
    def update_agent_system_message(agent: ConversableAgent, group_manager: GroupChatManager) -> None:
        from . import MakeService
        if agent.type == "FULL":
            # Define the new agent system message with placeholders filled in
            formatted_message = AgentService.FULL_AGENT_SYSTEM_MESSAGE.format(
                agent_name=agent.name,
                agent_description=MakeService._get_short_description(agent.description),
                group_name=group_manager.name,
                custom_instructions=agent.custom_system_message,
                group_stats=AgentService._generate_group_stats_text(group_manager)
            )
            agent.update_system_message(formatted_message)
        elif agent.type == "BASIC":
            # Define the new agent system message with placeholders filled in
            formatted_message = AgentService.BASIC_AGENT_SYSTEM_MESSAGE.format(
                agent_name=agent.name,
                agent_description=MakeService._get_short_description(agent.description),
                group_name=group_manager.name,
                custom_instructions=agent.custom_system_message
            )
            agent.update_system_message(formatted_message)
        