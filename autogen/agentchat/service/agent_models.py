from autogen.agentchat.service import UpsertAgentModel, AuthAgent, TERMINATE, OPENAI_FILES, OPENAI_RETRIEVAL, OPENAI_CODE_INTERPRETER, LOCAL_CODE_INTERPRETER, FUNCTION_CODER     
web_search_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_worker",
    category="information_retrieval",
    description="Executes search queries and compiles relevant information from diverse sources.",
    system_message="Read the conversation in the group. Execute the request queries and compile a comprehensive list of relevant information. Use files and retrieval for large data sets and knowledge base Q&A.",
    human_input_mode="NEVER",
    capability=OPENAI_FILES | OPENAI_RETRIEVAL,
    functions_to_add=["web_search"]
)

web_search_checker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_checker",
    category="information_retrieval",
    description="Critically evaluates the accuracy and relevance of search results, ensuring high-quality information.",
    system_message="Read the conversation in the group. Review the latest search results for accuracy and relevance. Approve or suggest modifications based on the search mood.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

web_search_planner_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_planner",
    category="information_retrieval",
    description="Designs and refines search queries based on specified criteria, ensuring optimal search results.",
    system_message="Read the conversation in the group. Extract the key search criteria and select the search mood: Strict, Relaxed, or Abstract. Create a few optimal search queries to enhance the search if necessary.",
    human_input_mode="NEVER",
    capability=0
)

web_search_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_manager",
    category="information_retrieval",
    description="Coordinates group activities, ensuring efficient collaboration and high-quality, clear, and comprehensive final outputs.",
    system_message="Read the conversation in the group. Coordinate the group's activities, monitor progress, and ensure the final output meets quality standards.",
    human_input_mode="NEVER",
    capability=0
)

plan_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="plan_worker",
    category="planning",
    description="Develops detailed, step-by-step plans for addressing complex problems.",
    system_message="Read the conversation in the group. Outline a detailed plan for provided problem, ensuring a step-by-step approach.",
    human_input_mode="NEVER",
    capability=0
)

plan_checker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="plan_checker",
    category="planning",
    description="Assesses plans for completeness, feasibility, and effectiveness.",
    system_message="Read the conversation in the group. Evaluate the proposed plan for completeness and feasibility. Provide feedback or approval.",
    human_input_mode="NEVER",
    capability=0
)

plan_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="plan_manager",
    category="planning",
    description="Oversee the planning process, ensuring effective collaboration and timely completion of plans.",
    system_message="Read the conversation in the group. Manage the planning process, ensuring collaboration and adherence to timelines.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

openai_code_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="openai_code_worker",
    category="programming",
    description="Develops code based on provided plans, focusing on functionality and adherence to specifications.",
    system_message="Read the conversation in the group. Query a tool to create and run code for the provided segment of the plan or otherwise the standalone task, focusing on functionality and specifications. Invoke the OpenAI Code Interpreter tool to run code in a sandbox.",
    human_input_mode="NEVER",
    capability=OPENAI_FILES | OPENAI_CODE_INTERPRETER
)

openai_code_checker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="openai_code_checker",
    category="programming",
    description="Ensures code quality through testing, review, and writing tests, maintaining high standards.",
    system_message="Read the conversation in the group. Conduct a thorough review and testing for the latest interpreter result. Provide feedback or approval.",
    human_input_mode="NEVER",
    capability=OPENAI_FILES | OPENAI_CODE_INTERPRETER
)

openai_code_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="openai_code_manager",
    category="programming",
    description="Coordinates coding activities, ensuring efficient progress and high-quality code development.",
    system_message="Read the conversation in the group. Oversee the coding process, track progress, and ensure code quality and deadline adherence.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

local_code_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="local_code_worker",
    category="programming",
    description="Develops code based on provided plans, focusing on functionality and adherence to specifications.",
    system_message="Read the conversation in the group. Create Python code block(s) through text-interaction, for the provided segment of the plan or otherwise the standalone task, focusing on functionality and specifications. You may manage outputs and internal state with files programmatically. Code in code blocks will automatically run when you provide the response.",
    human_input_mode="NEVER",
)

local_code_checker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="local_code_checker",
    category="programming",
    description="Ensures code quality through testing, review, and writing tests, maintaining high standards.",
    system_message="Read the conversation in the group. Conduct a thorough review and testing for the latest local interpreter result. You may write code like tests or debugging through code blocks. The code will automatically run upon your response. Provide feedback or approval.",
    human_input_mode="NEVER",
    capability=LOCAL_CODE_INTERPRETER
)

local_code_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="local_code_manager",
    category="programming",
    description="Coordinates coding activities, ensuring efficient progress and high-quality code development.",
    system_message="Read the conversation in the group. Oversee the coding process, track progress, and ensure code quality and deadline adherence.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

function_code_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="function_code_worker",
    category="programming",
    description="Specializes in creating reusable, efficient functions based on given requirements.",
    system_message="Read the conversation in the group. Develop a reusable function for the provided requirements, focusing on efficiency and adaptability.",
    human_input_mode="NEVER",
    capability=FUNCTION_CODER
)

function_checker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="function_checker",
    category="programming",
    description="Tests functions for reliability and provides feedback for enhancements.",
    system_message="Read the converation in the group. Test the created function for reliability and provide constructive feedback. Update the development status accordingly.",
    human_input_mode="NEVER",
    capability=FUNCTION_CODER
)

function_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="function_manager",
    category="programming",
    description="Ensures the development of high-quality, reliable functions, overseeing the entire creation process.",
    system_message="Read the conversation in the group. Manage the function creation process, ensuring quality, reliability, and adherence to requirements.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

api_caller_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="api_caller",
    category="communication",
    description="Handles the execution of API calls as defined in the OpenAPI specification.",
    system_message="Read the conversation in the group. As the api_caller_agent, your primary role is to execute API calls based on the provided OpenAPI SCHEMA. You need to interpret these specifications, construct the appropriate HTTP requests, and send them to the designated endpoints. Ensure that you handle different request methods (GET, POST, etc.), and accurately pass parameters and headers as required. After making an API call, forward the response to the api_tester for validation and further processing. Ask user to manually browse to configuration links as necessary to authenticate actions and ask for any relevant authentication info needed for API calls.",
    human_input_mode="ALWAYS",
    capability=TERMINATE,
    functions_to_add=["call_api_url"]
)

api_tester_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="api_tester",
    category="communication",
    description="Responsible for testing the endpoints found in the OpenAPI specification as well as auditing the responses from api_caller.",
    system_message="Read the conversation in the group. As the api_tester, your responsibility is to oversee the API interaction process. This includes receiving responses from the api_caller, validating these responses against expected outcomes, and ensuring they align with the OpenAPI SCHEMA. Also conduct thorough tests on endpoints in the SCHEMA to check for correctness, handle errors gracefully, and provide feedback for any necessary adjustments. Additionally, manage the workflow of API interactions, coordinating between different agents and functions to ensure smooth and efficient operations.",
    human_input_mode="NEVER",
    capability=TERMINATE,
    functions_to_add=["call_api_url"]
)
external_agent_models = [
    web_search_planner_model,
    web_search_worker_model,
    web_search_checker_model,
    web_search_manager_model,
    plan_worker_model,
    plan_checker_model,
    plan_manager_model,
    openai_code_manager_model,
    openai_code_worker_model,
    openai_code_checker_model,
    function_code_worker_model,
    function_checker_model,
    function_manager_model,
    local_code_worker_model,
    local_code_checker_model,
    local_code_manager_model,
    api_caller_model,
    api_tester_model
]
