from autogen.agentchat.service import UpsertGroupModel, AuthAgent
web_search_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_group",
    description="The web_search_group specializes in conducting comprehensive web searches, delivering well-structured and detailed information on diverse topics. It consists of web_search_planner, web_search_worker, web_search_checker, and web_search_manager. The planner formulates effective search queries, the agent executes these queries and gathers information, and the QA ensures accuracy and relevance. The manager oversees operations, ensuring smooth collaboration and that the final output is self-contained, clear, and ready for presentation to the calling group. The group operates under three search moods: 'Strict' for precise and specific queries, 'Relaxed' for broader searches, and 'Abstract' for conceptual and thematic searches. Only web_search_checker or web_search_manager can terminate the group.",
    agents_to_add=["web_search_planner", "web_search_worker", "web_search_checker", "web_search_manager"],
    locked = True
)

planning_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="planning_group",
    description="The Planning Group tackles problems by creating detailed, provided step-by-step, tree-of-thought / chain-of-thought plans for the task resolution. plan_worker will create the plan, plan_checker will check the plan and plan_manager will coordinate the group and ensure worker and checker work effectively to create an optimal detailed plan. Only plan_manager can terminate the group. The group consuming answers from planning likely will work in a chain-of-thought or tree-of-thought pattern to delegate tasks from the plan to other groups. Sometimes based on feedback from other groups during task delegation the plan will need to be updated, in which case the planner can be invoked to update a plan. You can use coding assistance to coordinate and manage files and documentation across the agent ecosystem.",
    agents_to_add=["plan_worker", "plan_checker", "plan_manager"],
    locked = True
)

coding_assistance_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="coding_assistance_group",
    description=("The Coding Assistant Group specializes in developing coding solutions guided by detailed, step-by-step plans, utilizing tree-of-thought or chain-of-thought methodologies. This group thrives in a Git-based development setting, focusing on software creation within a local repository while also accommodating the development of non-code related documentation such as project plans, design documents, API documentation, and other project-related materials."
                 "In instances where a plan is not provided, the group proactively requests one, except for straightforward requests. The group's collaboration is geared towards working on a remote GitHub repository, starting with setting up the repository through the setup_code_assistant function."
                 "Key responsibilities include validating all code and documentation before finalizing the group's tasks. This validation is essential for ensuring the quality and completeness of both code and related documents. Once the group's output is deemed acceptable, a pull request is created to merge the work into the remote repository."
                 "For smaller, independent functions or routines that are intended for future reuse, the function_creation_group is recommended."
                 "The group's workflow mandates that the output, whether code or documentation, is acknowledged through merging into the remote repository before the group's closure is accepted. This process ensures that the contributions of the Coding Assistant Group are properly integrated and recognized within the broader project context."),
    agents_to_add=["code_assistant_worker", "code_assistant_checker", "code_assistant_manager"],
    locked = True
)

functions_coding_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="function_creation_group",
    description="The Function Creation Group mirrors the structure of the Local and OpenAI Coding group but specializes in developing, testing, and refining reusable functions, ensuring they meet high standards of quality and efficiency. function_code_worker will create the function, function_checker will sanity check the function fields and test the function execution. function_checker will also transition the function from development to testing and finally to acceptance once accepted. function_manager will oversee the creation and testing process to ensure it goes smoothly. Use this group to make small functions and routines within a broader context to re-use in the future. Not meant for code applications end-to-end, just isolated routines. For applications, use coding_assistance_group.",
    agents_to_add=["function_code_worker", "function_checker", "function_manager"],
    locked = True
)

zapier_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="zapier_automation_group",
    description="The Zapier Automation Group is dedicated to harnessing the power of APIs with almost infinite capabilities for seamless workflow automation and integration via Zapier. Zapier is an API aggregator that can solve almost any API task to external systems. It specializes in connecting a wide array of applications, facilitating data transfer, and automating tasks across platforms such as Google Workspace, Microsoft Office 365, Salesforce, Slack, Trello, Shopify, Mailchimp, Asana, QuickBooks, HubSpot, Dropbox, Airtable, Zendesk, WordPress, and Twitter. We focus on setting up and managing Zaps, ensuring robust API interactions, and optimizing processes for efficiency and reliability. Key activities include API configuration, testing Zapier integrations, and customizing automation to align with specific workflow requirements. You can use coding assistance to coordinate and manage files and documentation or output across the agent ecosystem.",
    agents_to_add=["zapier_api_manager", "zapier_api_caller", "zapier_api_tester"],
    locked=True
)

external_group_models = [
    web_search_group_model,
    planning_group_model,
    coding_assistance_group_model,
    functions_coding_group_model,
    zapier_group_model
]
