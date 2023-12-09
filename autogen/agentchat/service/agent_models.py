from autogen.agentchat.service import UpsertAgentModel, AuthAgent, TERMINATE, OPENAI_FILES, OPENAI_RETRIEVAL, OPENAI_CODE_INTERPRETER, CODING_ASSISTANCE, FUNCTION_CODER     
web_search_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_worker",
    category="information_retrieval",
    description="Executes search queries and compiles relevant information from diverse sources. Usually works in web_search_group alongside web_search_checker, web_search_planner and web_search_manager.",
    system_message="Read the conversation in the group. Usually you work in the web_search_group. Execute the request queries and compile a comprehensive list of relevant information. Use files and retrieval for large data sets and knowledge base Q&A.",
    human_input_mode="NEVER",
    capability=OPENAI_FILES | OPENAI_RETRIEVAL,
    functions_to_add=["web_search"]
)

web_search_checker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_checker",
    category="information_retrieval",
    description="Search result critic. Usually works in web_search_group alongside web_search_worker, web_search_planner and web_search_manager.",
    system_message="Read the conversation in the group. Usually you work in the web_search_group. Review the latest search results for accuracy and relevance. Ensure to default to use the latest information by date. Critically evaluate the accuracy and relevance of search results, ensuring high-quality information. Approve or suggest modifications based on the search mood.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

web_search_planner_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_planner",
    category="information_retrieval",
    description="Designs and refines search queries based on specified criteria, ensuring optimal search results. Usually works in web_search_group alongside web_search_worker, web_search_checker and web_search_manager.",
    system_message="Read the conversation in the group. Usually you work in the web_search_group. Extract the key search criteria and select the search mood: Strict, Relaxed, or Abstract. Create a few optimal search queries to enhance the search if necessary.",
    human_input_mode="NEVER",
    capability=0
)

web_search_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_manager",
    category="information_retrieval",
    description="Coordinates group activities, ensuring efficient collaboration and high-quality, clear, and comprehensive final outputs. Usually works in web_search_group alongside web_search_worker, web_search_checker and web_search_planner.",
    system_message="Read the conversation in the group. Usually you work in the web_search_group. Coordinate the group's activities, monitor progress, and ensure the final output meets quality standards. You will yourself double check against search results.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

plan_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="plan_worker",
    category="planning",
    description="Develops detailed, step-by-step plans for addressing complex problems. Usually works in planning_group alongside plan_manager and plan_checker.",
    system_message="Read the conversation in the group. Usually you work in the planning_group. Outline a detailed plan for provided problem, ensuring a step-by-step approach. To manage efficient creation of documentation you may want to use coding assistance via git repository.",
    human_input_mode="NEVER",
    capability=0
)

plan_checker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="plan_checker",
    category="planning",
    description="Assesses plans for completeness, feasibility, and effectiveness. Usually works in planning_group alongside plan_manager and plan_worker.",
    system_message="Read the conversation in the group. Usually you work in the planning_group. Evaluate the proposed plan for completeness and feasibility. Provide feedback or approval. To manage efficient creation of documentation you may want to use coding assistance via git repository.",
    human_input_mode="NEVER",
    capability=0
)

plan_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="plan_manager",
    category="planning",
    description="Oversee the planning process, ensuring effective collaboration and timely completion of plans. Usually works in planning_group alongside plan_checker and plan_worker.",
    system_message="Read the conversation in the group. Usually you work in the planning_group. Manage the planning process, ensuring collaboration and adherence to timelines. To manage efficient creation of documentation you may want to use coding assistance via git repository.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

openai_code_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="openai_code_worker",
    category="programming",
    description="Enabled OpenAI files and interpreter tools to create/run code and provide responses through natural language. Ideal for algorithmics, data science, visualization or mathematical calculations that require code generation to solve.",
    system_message="In natural language request, explicitly state that you are invoking the OpenAI interpreter (outputting OpenAI files as needed for example visualization or analysis), describing what code is needed and expected response. This will create and run code in a sandbox in OpenAI servers and return the code response.",
    human_input_mode="NEVER",
    capability=OPENAI_FILES | OPENAI_CODE_INTERPRETER
)

openai_retrieval_rag_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="openai_retrieval_rag_worker",
    category="programming",
    description="Enabled RAG with OpenAI files and to answer questions against a knowledge base using natural language.",
    system_message="In natural language request, explicitly state that you are invoking the OpenAI retrieval tool to answer questions about a knowledge base. The knowledge base comes from OpenAI files which is indexed in a database automatically by specifying the file id's in the text-interaction. This will index the file contents specified, create a RAG, do semantic searches based on the knowledge in OpenAI servers and return the summarized response.",
    human_input_mode="NEVER",
    capability=OPENAI_FILES | OPENAI_RETRIEVAL
)

code_assistant_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="code_assistant_worker",
    category="programming",
    description="Develops code based on provided plans, focusing on functionality and adherence to specifications. Usually works in coding_assistance_group alongside code_assistant_manager and code_assistant_checker.",
    system_message="Read the conversation in the group. Use the function you are given. Usually you work in the coding_assistance_group. Based on the plan, instruct the code assistant to create code through the 'message' parameter. You will manage the code assistant state through the function parameters provided. Ensure repository is setup already remotely and locally prior to working. Add files to work on as well as you go. When constructing the message to code assistant, make sure to tell it to return the full code and not comments replacing code.",
    capability=CODING_ASSISTANCE,
    human_input_mode="NEVER",
    functions_to_add=["upsert_coding_assistant", "get_coding_assistant_info", "discover_coding_assistants"]
)

code_assistant_checker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="code_assistant_checker",
    category="programming",
    description="Ensures code quality through code review, feedback to coder and writing tests, maintaining high standards. Usually works in coding_assistance_group alongside code_assistant_worker and code_assistant_manager.",
    system_message="Read the conversation in the group. Usually you work in the coding_assistance_group. Use the functions you are given. Ensure a remote git repository is setup prior to working, ask for username and auth token as needed to setup the assistant. Add files to work on as well as you go. Conduct a thorough review and testing for the code in the local git repository. You may write code like tests or debugging through code assistant functions. You should approve the quality of the code prior to group termination. For acceptance there should be tests and test criteria. Upon acceptance you should create a PR to the remote repository. Example git auth URL: https://user:<MYTOKEN>@github.com/repository/repo.git. When constructing the message to code assistant, make sure to tell it to return the full code and not comments replacing code. Once code assistant is setup, you can send messages to the code assistant to do the work.",
    human_input_mode="ALWAYS",
    capability=CODING_ASSISTANCE,
    functions_to_add=["upsert_coding_assistant", "get_coding_assistant_info", "discover_coding_assistants"]
)

code_assistant_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="code_assistant_manager",
    category="programming",
    description="Coordinates coding activities, ensuring efficient progress and high-quality code development. Usually works in coding_assistance_group alongside code_assistant_worker and code_assistant_checker.",
    system_message="Read the conversation in the group. Usually you work in the coding_assistance_group. Oversee the coding process, track progress, and ensure code quality and deadline adherence. Start with code_assistant_checker to make sure a remote repo is provided/created by asking for username and auth token, then create if needed and clone it remotely and begin working.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

function_code_worker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="function_code_worker",
    category="programming",
    description="Specializes in creating reusable, efficient functions based on given requirements. Usually works in function_creation_group alongside function_checker and function_manager.",
    system_message="Read the conversation in the group. Usually you work in the function_creation_group. Develop a reusable function for the provided requirements, focusing on efficiency and adaptability. For complex functions you may need to use coding assistance to provide you with working code to work into a function.",
    human_input_mode="NEVER",
    capability=FUNCTION_CODER
)

function_checker_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="function_checker",
    category="programming",
    description="Tests functions for reliability and provides feedback for enhancements. Usually works in function_creation_group alongside function_code_worker and function_manager.",
    system_message="Read the converation in the group. Usually you work in the function_creation_group. Test the created function for reliability and provide constructive feedback. Update the development status accordingly. For complex functions you may need to use coding assistance to provide you with working code to work into a function.",
    human_input_mode="NEVER",
    capability=FUNCTION_CODER
)

function_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="function_manager",
    category="programming",
    description="Ensures the development of high-quality, reliable functions, overseeing the entire creation process. Usually works in function_creation_group alongside function_checker and function_code_worker.",
    system_message="Read the conversation in the group. Usually you work in the function_creation_group. Manage the function creation process, ensuring quality, reliability, and adherence to requirements. For complex functions you may need to use coding assistance to provide you with working code to work into a function.",
    human_input_mode="NEVER",
    capability=TERMINATE
)

zapier_api_caller_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="zapier_api_caller",
    category="communication",
    description="Handles the execution of Zapier API calls. Zapier is an API aggregator that can solve almost any API task to external systems. Usually works in zapier_automation_group alongside zapier_api_tester and zapier_api_manager",
    system_message="Read the conversation in the group. Usually you work in the zapier_automation_group. You will use the tools you have been given, you will be directed by zapier_api_manager to convert directions to actions within your tools. You should simply make the function calls and respond with the data for others in the group to analyze.",
    human_input_mode="ALWAYS",
    capability=TERMINATE,
    functions_to_add=["zapier_api_check", "zapier_api_get_configuration_link", "zapier_api_list_exposed_actions", "zapier_api_execute_action", "zapier_api_execute_log", "zapier_api_create_action"]
)

zapier_api_tester_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="zapier_api_tester",
    category="communication",
    description="Responsible for testing the Zapier API queries and responses and offering feedback to zapier_api_caller. Usually works in zapier_automation_group alongside zapier_api_manager and zapier_api_caller.",
    system_message="Read the conversation in the group. Use the tools given to you to help use Zapier in production setting to solve your task.",
    human_input_mode="ALWAYS",
    functions_to_add=["zapier_api_check", "zapier_api_get_configuration_link", "zapier_api_list_exposed_actions", "zapier_api_execute_action", "zapier_api_execute_log", "zapier_api_create_action"]
)
zapier_api_manager_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="zapier_api_manager",
    category="communication",
    description="Responsible for managing and summarizing responses of the Zapier API. You need an API KEY so ask the user for this first (user can create one here https://actions.zapier.com/credentials/). Usually works in zapier_automation_group alongside zapier_api_tester and zapier_api_caller.",
    system_message=(
       "Read the conversation in the group. Usually you work in the zapier_automation_group. Ask for the API KEY from the user. Your goal is to convert your task into actions through Zapier to solve through external APIs. If you think you need multiple actions, make them first and run them after. Once you have an API KEY you can use zapier_api_caller to generally:\n"
        "1. List AI Actions\n"
        "2. Create an AI Action. Ask the user for confirmation that an Action was setup in their Zapier account after URL given to them via zapier_api_create_action.\n"
        "3. Preview an AI Action execution. This is to see if all fields auto-filled by AI match your expectations.\n"
        "4. Execute an AI Action.\n"
        "5. Read AI Action logs as needed\n"
    ),
    human_input_mode="ALWAYS",
    capability=TERMINATE,
    functions_to_add=["zapier_api_check"]
)
external_agent_models = [
    web_search_planner_model,
    web_search_worker_model,
    web_search_checker_model,
    web_search_manager_model,
    plan_worker_model,
    plan_checker_model,
    plan_manager_model,
    openai_code_worker_model,
    openai_retrieval_rag_worker_model,
    function_code_worker_model,
    function_checker_model,
    function_manager_model,
    code_assistant_worker_model,
    code_assistant_checker_model,
    code_assistant_manager_model,
    zapier_api_caller_model,
    zapier_api_manager_model,
    zapier_api_tester_model
]
