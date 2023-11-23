from autogen.agentchat.service import UpsertAgentModel, AuthAgent, MANAGEMENT, INFO, CODE_INTERPRETER, FILES, RETRIEVAL     
web_search_agent_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_agent",
    category="information_retrieval",
    description="Uses tools to find information through search engines.",
    system_message="As the web_search_agent, your role is to conduct thorough online searches based on given queries. Focus on extracting key information such as main points, publication dates, sources, and provide direct links to the sources. Your goal is to provide a comprehensive overview of search results. Work closely with the web_search_planner for effective query formulation and pass your findings to web_search_qa for a final quality check. Remember, accuracy and relevance are paramount.",
    human_input_mode="NEVER",
    capability=INFO | FILES | RETRIEVAL,
    functions_to_add=["web_search"]
)

web_search_qa_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_qa",
    category="planning",
    description="Quality assurance on web search results from web_search_agent.",
    system_message="As the web_search_qa, you are responsible for ensuring the accuracy, relevance, and completeness of information retrieved by the web_search_agent. Critically evaluate the data provided, ensuring they offer a comprehensive view of the topic. If the information is lacking or not up-to-date, instruct the web_search_agent to refine the search. Your final task is to detail all verified information, ensuring it provides a complete understanding of the topic at hand. You are the final checkpoint before the information is relayed back to the requester.",
    human_input_mode="NEVER",
    capability=INFO
)

web_search_planner_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_planner",
    category="planning",
    description="Take a web search query and come up with more related queries to make a more sparse search for best possible results.",
    system_message="As the web_search_planner, your expertise lies in developing effective and diverse search queries based on the initial request. Analyze the search request and create a set of targeted queries that will yield comprehensive results across various aspects of the topic. Your queries should guide the web_search_agent in covering the breadth and depth of the topic. Coordinate with the web_search_agent to refine queries as needed, ensuring a broad yet focused search approach. Your role is crucial in setting the direction for an effective search strategy.",
    human_input_mode="NEVER",
    capability=INFO
)

external_agent_models = [
    web_search_planner_model,
    web_search_agent_model,
    web_search_qa_model
]
