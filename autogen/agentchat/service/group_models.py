from autogen.agentchat.service import UpsertGroupModel, AuthAgent
web_search_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_group",
    description="The web_search_group specializes in conducting comprehensive web searches, delivering well-structured and detailed information on diverse topics. It consists of the web_search_planner, web_search_worker, web_search_checker, and web_search_manager. The planner formulates effective search queries, the agent executes these queries and gathers information, and the QA ensures accuracy and relevance. The manager oversees operations, ensuring smooth collaboration and that the final output is self-contained, clear, and ready for presentation to the calling group. The group operates under three search moods: 'Strict' for precise and specific queries, 'Relaxed' for broader searches, and 'Abstract' for conceptual and thematic searches. Only web_search_checker can terminate the group.",
    agents_to_add=["web_search_planner", "web_search_worker", "web_search_checker", "web_search_manager"],
    locked = True
)

planning_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="planning_group",
    description="The Planning Group tackles problems by creating detailed, step-by-step plans for their resolution. plan_worker will create the plan, plan_checker will check the plan and plan_manager will coordinate the group and ensure worker and checker work effectively to create an optimal detailed plan. Only plan_manager can terminate the group.",
    agents_to_add=["plan_worker", "plan_checker", "plan_manager"],
    locked = True
)

openai_coding_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="openai_coding_group",
    description="The OpenAI Coding Group develops code solutions based on provided step-by-step plans. In the absence of a plan, the group is proactive in requesting one unless its a simple request. openai_code_worker will write the code, openai_code_checker will run and be quality assurance as well as write tests and openai_code_manager will coordinate the group and ensure worker and checker work effectively to create optimal working code. Only openai_code_manager can terminate the group. Create a function if code created is meant to be reusable through the 'function_creation_group'.",
    agents_to_add=["openai_code_worker", "openai_code_checker", "openai_code_manager"],
    locked = True
)

local_coding_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="local_coding_group",
    description="The Local Coding Group mirrors the structure of the OpenAI Coding Group but focuses on local development environments and emphasizes the creation of reusable functions through the 'function_creation_group'.",
    agents_to_add=["local_code_worker", "local_code_checker", "local_code_manager"],
    locked = True
)

functions_coding_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="function_creation_group",
    description="The Function Creation Group mirrors the structure of the Local and OpenAI Coding group but specializes in developing, testing, and refining reusable functions, ensuring they meet high standards of quality and efficiency. function_code_worker will create the function, function_checker will sanity check the function fields and test the function execution. function_checker will also transition the function from development to testing and finally to acceptance once accepted. function_manager will oversee the creation and testing process to ensure it goes smoothly.",
    agents_to_add=["function_code_worker", "function_checker", "function_manager"],
    locked = True
)

zapier_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="zapier_automation_group",
    description=(
        "The Zapier Automation Group is dedicated to harnessing the power of APIs with almost infinite capabilities for seamless workflow automation and integration via Zapier. Zapier is an API aggregator that can solve almost any API task to external systems. It specializes in connecting a wide array of applications, facilitating data transfer, and automating tasks across platforms such as Google Workspace, Microsoft Office 365, Salesforce, Slack, Trello, Shopify, Mailchimp, Asana, QuickBooks, HubSpot, Dropbox, Airtable, Zendesk, WordPress, and Twitter. We focus on setting up and managing Zaps, ensuring robust API interactions, and optimizing processes for efficiency and reliability. Key activities include API configuration, testing Zapier integrations, and customizing automation to align with specific workflow requirements.\n\n"
    ),
    agents_to_add=["zapier_api_manager", "zapier_api_caller", "zapier_api_tester"],
    locked=True
)

external_group_models = [
    web_search_group_model,
    planning_group_model,
    openai_coding_group_model,
    local_coding_group_model,
    functions_coding_group_model,
    zapier_group_model
]
