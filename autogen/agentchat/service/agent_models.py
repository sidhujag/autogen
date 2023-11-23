from autogen.agentchat.service import UpsertAgentModel, AuthAgent, TERMINATE, FILES, RETRIEVAL     
web_search_agent_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_agent",
    category="information_retrieval",
    description="Executes detailed web searches based on queries, focusing on gathering comprehensive, relevant information, and presenting it with clear references to sources. Extracts key information like titles, snippets, links, and dates.",
    system_message="Conduct thorough online searches based on the provided queries. Focus on extracting key information such as main points, publication dates, sources, and provide direct links. Collaborate with the web_search_planner for query refinement and pass your findings to web_search_qa for quality assurance.",
    human_input_mode="NEVER",
    capability=FILES | RETRIEVAL,
    functions_to_add=["web_search"]
)

web_search_qa_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_qa",
    category="information_retrieval",
    description="Ensures the accuracy and relevance of information retrieved by the web_search_agent and prepares a comprehensive summary of the findings.",
    system_message="Review the information provided by the web_search_agent for accuracy and relevance. Prepare a detailed summary of the key findings, ensuring it is comprehensive and ready for presentation to the calling group. Only you can terminate this group.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

web_search_planner_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_planner",
    category="information_retrieval",
    description="Creates targeted search queries based on initial requests to guide the web_search_agent in covering various aspects of the topic.",
    system_message="Develop effective search queries based on the initial request. Work with the web_search_agent to ensure a broad yet focused search approach. Coordinate with the web_search_manager for strategy refinement.",
    human_input_mode="NEVER",
    capability=0
)

web_search_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_manager",
    category="information_retrieval",
    description="Oversees the web_search_group's operations, ensuring efficient collaboration and that the final output is comprehensive and well-structured for the calling group.",
    system_message="Coordinate the activities of the web_search_group. Ensure the final output is comprehensive, well-structured, and ready for delivery to the calling group. Facilitate effective communication and integration of feedback within the group.",
    human_input_mode="NEVER",
    capability=0
)

plan_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="plan_worker",
    category="planning",
    description="Creates detailed step-by-step plan to solve the problem you have been tasked with.",
    system_message="You are a world class problem solving machine and task planner. Creates detailed step-by-step plan to solve the problem you have been tasked with.",
    human_input_mode="NEVER",
    capability=0
)

plan_checker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="plan_checker",
    category="planning",
    description="Check the work of plan_worker and revise or give feedback.",
    system_message="You are a world class plan checker. Give valuable insight and feedback to plan_worker based on his plan to solve the problem.",
    human_input_mode="NEVER",
    capability=0
)

plan_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="plan_manager",
    category="planning",
    description="Oversees the planning_group's operations, ensuring efficient collaboration and that the final output is comprehensive and well-structured for the calling group.",
    system_message="Coordinate the activities of the planning_group. Ensure the final output is comprehensive, well-structured, and ready for delivery to the calling group. Facilitate effective communication and integration of feedback within the group. Only you can terminate the group.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

external_agent_models = [
    web_search_planner_model,
    web_search_agent_model,
    web_search_qa_model,
    web_search_manager_model,
    plan_worker_model,
    plan_checker_model,
    plan_manager_model
]
