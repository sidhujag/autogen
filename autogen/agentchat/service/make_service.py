import re
from typing import List, Optional, Union
from .. import DiscoverableConversableAgent
from autogen import OpenAIWrapper, config_list_from_json

class MakeService:
    
    AGENT_SYSTEM_MESSAGE: str = """AUTONOMOUS AI AGENT

- Communication Capabilities: Can build relationships with and be part of an organizational hierarchical structure with other agents.
- Problem-Solving: Solve problems step-by-step.
- Functions: Utilize provided functions in real-world contexts.
- Discovery: Discover agents and communicate effectively by providing context.
- Relationship-Building: Form communication and delegation through messages as a dependency graph, with established incoming connections from those who requested assistance and outgoing connections to dependencies for solving problems.
- Coding: Able to write and execute code directly from conversation interactions in a secure sandbox environment. External packages must be installed via code execution.
- Agent & Function Discovery: Can discover new agents and functions and introduce capabilities to others.

Communications must be clear, contextual, and directed towards problem-solving within the established hierarchical structure.
Respond with only 'TERMINATE' when you are terminating."""
    AGENT_REGISTRY: dict[str, DiscoverableConversableAgent] = {}
    @staticmethod
    def get_service(service_type):
        from . import AgentService, FunctionsService
        if service_type == 'agent':
            return AgentService()
        elif service_type == 'function':
            return FunctionsService()

    @staticmethod
    def update_agent(agent, backend_agent):
        from . import FunctionsService, AddFunctionModel
        agent.update_system_message(backend_agent.system_message)
        MakeService.update_system_message(agent)
        if len(backend_agent.functions) > 0:
            for function in backend_agent.functions:
                FunctionsService.define_function_internal(agent, AddFunctionModel(**function, auth=agent.auth))
            # re-init client because functions were passed defined
            agent.client = OpenAIWrapper(**agent.llm_config)
        MakeService.AGENT_REGISTRY[agent.name] = agent
    
    
    @staticmethod
    def _update_system_message_with_stats(agent: DiscoverableConversableAgent):
        # Define a pattern to identify the communication stats section
        pattern = re.compile(
            r"COMMUNICATION STATS:\n.*?(?=\n\n|$)", re.DOTALL
        )
        # Generate the new communication stats text
        new_stats = MakeService._generate_communication_stats_text(agent)
        
        # If the stats section already exists, replace it
        if pattern.search(agent.system_message):
            agent.update_system_message(pattern.sub(new_stats, agent.system_message))
        else:
            # Otherwise, append the new stats to the system message
            agent.update_system_message(agent.system_message + f"\n\n{new_stats}")

    @staticmethod
    def _generate_communication_stats_text(agent: DiscoverableConversableAgent) -> str:
        incoming_communications = "\n".join(
            f"- {agent_name}: {details.count} message(s), Description: {details.description}"
            for agent_name, details in agent.incoming.items()
        )
        outgoing_communications = "\n".join(
            f"- {agent_name}: {details.count} message(s), Description: {details.description}"
            for agent_name, details in agent.outgoing.items()
        )
        communications = f"""
        COMMUNICATION STATS:
        Incoming communications (list of agents and count of incoming messages from them):
        {incoming_communications}
        Outgoing communications (list of agents and count of outgoing messages to them):
        {outgoing_communications}
        """

        return communications.strip()
    
    @staticmethod
    def create_system_message(backend_agent) -> str:
        # Generate the updated communication stats
        comms_stats_text = MakeService._generate_communication_stats_text(backend_agent)

        # Create the full system message by combining the initial message, the standard prompt, and the comms stats
        full_system_message = f"{backend_agent.system_message}\n{MakeService.AGENT_SYSTEM_MESSAGE}\n{comms_stats_text}"

        # Return the full system message
        return full_system_message
    
    @staticmethod
    def update_system_message(agent: DiscoverableConversableAgent) -> str:
        # Check if AGENT_SYSTEM_MESSAGE is already in the system_message.
        if MakeService.AGENT_SYSTEM_MESSAGE not in agent.system_message:
            # If not, append it.
            agent.update_system_message(agent.system_message + f"\n\n{MakeService.AGENT_SYSTEM_MESSAGE}")

        # Update the communication stats in the system message.
        MakeService._update_system_message_with_stats(agent)

    @staticmethod
    def _create_agent(backend_agent) -> DiscoverableConversableAgent:
        config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
        agent = DiscoverableConversableAgent(
                name=backend_agent.name,
                human_input_mode=backend_agent.human_input_mode,
                default_auto_reply=backend_agent.default_auto_reply,
                system_message=MakeService.create_system_message(backend_agent),
                llm_config={"config_list": config_list, "api_key": backend_agent.auth.api_key},
                incoming=backend_agent.incoming,
                outgoing=backend_agent.outgoing
            )
        return agent

    @staticmethod
    def make_agent(backend_agent, llm_config: Optional[Union[dict, bool]] = None):
        from . import FunctionsService, AddFunctionModel
        agent = MakeService._create_agent(backend_agent)
        agent.description = backend_agent.description
        agent.auth = backend_agent.auth
        if llm_config:
            agent.llm_config.update(llm_config)
        if len(backend_agent.functions) > 0:
            for function in backend_agent.functions:
                FunctionsService.define_function_internal(agent, AddFunctionModel(**function, auth=agent.auth))
            # re-init client because functions were passed defined
            agent.client = OpenAIWrapper(**agent.llm_config)
        MakeService.AGENT_REGISTRY[agent.name] = agent
        return agent, None
    
    @staticmethod
    def upsert_agents(upsert_models):
        from . import BackendService, GetAgentModel
        # Step 1: Upsert all agents in batch
        err = BackendService.upsert_backend_agents(upsert_models)
        if err:
            return None, err

        # Step 2: Retrieve all agents from backend in batch
        get_agent_models = [GetAgentModel(auth=model.auth, name=model.name) for model in upsert_models]
        backend_agents, err = BackendService.get_backend_agents(get_agent_models)
        if err:
            return None, err

        # Step 3: Update local agent registry
        successful_agents = []
        for backend_agent in backend_agents:
            agent = MakeService.AGENT_REGISTRY.get(backend_agent.name)
            if agent is None:
                agent, err = MakeService.make_agent(backend_agent)
                if err is not None:
                    return None, err
            else:
                MakeService.update_agent(agent, backend_agent)
            successful_agents.append(agent)
        return successful_agents, None
