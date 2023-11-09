from .. import ConversableAgent, GroupChatManager
from typing import List, Optional, Union
from autogen import OpenAIWrapper
from autogen.agentchat.service.function_specs import function_specs

class AgentService:
    AGENT_SYSTEM_MESSAGE: str = """Agent, you are a cog in a complex AI hierarchy, designed to solve tasks collaboratively. Solve tasks step-by-step.

Agent name and Group: Your name: {agent_name}, description: {agent_description}, group: {group_name}

Communication and Collaboration: The agent's primary function is to communicate within a group setting for problem-solving, highlighting the importance of clear and purposeful exchanges.

Agent identity and Context: Each message sent to the group will identify the sender and the group context, ensuring that communications are traceable and relevant.

Group stats and Context: Group stats are tracked and given in your system prompt. These stats are available for any other group via the get_group_info function. Useful for your self-discovery.

Agent, Function and Group Discovery: The Agent can discover functions to add to themselves, discover other agents to add to a group or discover groups to delegate tasks to or add agents to. Any agent can create/update any function or group. If error happens in a function, fix the function instead of making a new one. The function name is a pointer to the function inside an agent and likewise for an agent inside a group. You don't need to re-add pointers as the underlying changes.

Task Orientation: The agent's communications should be direct and focused on resolving the given tasks, avoiding unnecessary dialogue.

Coding Abilities: The agent's ability to write and execute code within conversations is emphasized, enhancing their problem-solving capabilities. Any code blocks will be auto-executed by the system and code output sent back to you.

Network Dependency and Role: The agent is reminded of their interdependent role within the AI network, where mutual reliance is key to the system's functionality.

Group Engagement and Delegation: The agent is instructed to communicate with groups (not individuals), maintaining collective context and ensuring task delegation is clear and closed-loop.

Speaker Selection: The process of selecting the next speaker within a group is mentioned as a means to maintain order in conversations.

Task Delegation and Closure: Prioritize clear delegation of tasks to other groups. Before concluding any interaction with a 'TERMINATE' signal, ensure that the initiating group's query is satisfactorily addressed, maintaining a closed-loop communication cycle.

Monitoring and Governance: The agent is expected to adhere to the network's governance, with an emphasis on data integrity and efficiency.

Emergence and Innovation: The agent is considered an integral part of the network's intelligence and is encouraged to adapt and evolve to foster collective growth and innovation.

Efficiency in Discourse: The agent is directed to engage in conversations that directly address the task at hand, staying on point and avoiding tangential discussions.

Custom instructions: {custom_instructions}

GROUP STATS
{group_stats}

Reply with only "TERMINATE" on success condition. Try not to give up, you can solve almost anything through coding. Only terminate on failure condition if you are really sure you can't solve through existing functions, groups, agents or creating custom code with multiple tries. When doing so stay on topic though, don't change focus. If you have nothing to say about the topic just say so.
"""
    @staticmethod
    def get_agent(agent_model) -> ConversableAgent:
        from . import BackendService, MakeService
        agent: ConversableAgent = MakeService.AGENT_REGISTRY.get(agent_model.name)
        if agent is None:
            backend_agent, err = BackendService.get_backend_agents([agent_model])
            if err is None and len(backend_agent) > 0:
                agent, err = AgentService.make_agent(backend_agent[0])
                if err is not None:
                    MakeService.AGENT_REGISTRY[agent_model.name] = agent
        return agent

    @staticmethod
    def discover_agents(sender: ConversableAgent, query: str, category: str = None) -> str:
        from . import BackendService, DiscoverAgentsModel
        if sender is None:
            return "Sender not found"
        response, err = BackendService.discover_backend_agents(DiscoverAgentsModel(auth=sender.auth, query=query,category=category))
        if err is not None:
            return f"Could not discover agents: {err}"
        return response

    @staticmethod
    def upsert_agent(sender: ConversableAgent, name: str, description: str = None, system_message: str = None, functions_to_add: List[str] = None,  functions_to_remove: List[str] = None, category: str = None) -> str: 
        from . import UpsertAgentModel
        if sender is None:
            return "Sender not found"
        agent, err = AgentService.upsert_agents([UpsertAgentModel(
            auth=sender.auth,
            name=name,
            description=description,
            system_message=system_message,
            functions_to_add=functions_to_add,
            functions_to_remove=functions_to_remove,
            category=category
        )])
        if err is not None:
            return f"Could not upsert agent: {err}"
        return "Agent upserted!"

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
        # register the base functions for every agent
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
            return None, "Could not make agent"
        agent.description = backend_agent.description
        agent.custom_system_message = agent.system_message
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
        if err:
            return None, err

        # Step 2: Retrieve all agents from backend in batch
        get_agent_models = [GetAgentModel(auth=model.auth, name=model.name) for model in upsert_models]
        backend_agents, err = BackendService.get_backend_agents(get_agent_models)
        if err:
            return None, err
        if len(backend_agents) == 0:
            return None, "Could not fetch agents from backend"

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
        # Define the new agent system message with placeholders filled in
        formatted_message = AgentService.AGENT_SYSTEM_MESSAGE.format(
            agent_name=agent.name,
            agent_description=MakeService._get_short_description(agent.description),
            group_name=group_manager.name,
            custom_instructions=agent.custom_system_message,
            group_stats=AgentService._generate_group_stats_text(group_manager)
        )
        agent.update_system_message(formatted_message)