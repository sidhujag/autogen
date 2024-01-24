from autogen.agentchat.service import UpsertGroupModel, AuthAgent
web_search_group_model = UpsertGroupModel(
    name="web_search_group",
    description="The web_search_group specializes in conducting comprehensive web searches, delivering well-structured and detailed information on diverse topics. It consists of web_search_planner, web_search_worker, web_search_checker, and web_search_manager. The planner formulates effective search queries, the agent executes these queries and gathers information, and the QA ensures accuracy and relevance. The manager oversees operations, ensuring smooth collaboration and that the final output is self-contained, clear, and ready for presentation to the calling group. Only web_search_checker or web_search_manager can terminate the group. The following agents are in your group you can refer to them by name in your responses to communicate a message to them: web_search_planner, web_search_worker, web_search_checker, web_search_manager",
    agents_to_add=["web_search_planner", "web_search_worker", "web_search_checker", "web_search_manager"],
    locked = True
)

planning_group_model = UpsertGroupModel(
    name="planning_group",
    description="The Planning Group tackles problems by creating detailed, provided step-by-step, tree-of-thought / chain-of-thought plans for the task resolution. plan_worker will create the plan, plan_checker will check the plan and plan_manager will coordinate the group and ensure worker and checker work effectively to create an optimal detailed plan. Only plan_manager can terminate the group. The group consuming answers from planning likely will work in a chain-of-thought or tree-of-thought pattern to assign tasks from the plan to other groups. Sometimes based on feedback from other groups during task assignment the plan will need to be updated, in which case the planner can be invoked to update a plan. For software designing and planning there is a software_design_documentation_group. The following agents are in your group you can refer to them by name in your responses to communicate a message to them: plan_worker, plan_checker, plan_manager",
    agents_to_add=["plan_worker", "plan_checker", "plan_manager"],
    locked = True
)

software_design_documentation_group_model = UpsertGroupModel(
    name="software_design_documentation_group",
    description=("The Software Design Documentation Group specializes in developing software design by creating documentation such as project plans, design documents such as PRD, API documentation, and other project-related materials. Create product goals, user stories, competitive analysis (can leverage web research), requirements analysis, UI/UX design considerations. \n"
                 "The following agents are in your group you can refer to them by name in your responses to communicate a message to them: software_design_documentation_worker, software_design_documentation_reviewer, software_design_documentation_manager \n"
                 "Naturally feeds into the coding step by the software_coding_group. \n"
                 "This group only uses existing assitants and repositories and does not create ones ones. The software_coding_group can create new ones. \n"
                 "Make sure to create the relevant designs in the software_design_documentation_worker system message (all 18 steps). Note the design files are pre-created when repository is setup. Reference the associated file when making the change so the code assistant can know which file to work on. Use command_message with send_command_to_coding_assistant for each design step unless its done already. \n"
                 "Uses natural language to create or update documentation files."),
    agents_to_add=["software_design_documentation_worker", "software_design_documentation_reviewer", "software_design_documentation_manager"],
    locked = True
)

software_coding_group_model = UpsertGroupModel(
    name="software_coding_group",
    description=("The Software Coding Group specializes in developing software solutions through using code assistants guided by detailed, step-by-step plans, utilizing tree-of-thought or chain-of-thought methodologies. \n"
                 "The following agents are in your group you can refer to them by name in your responses to communicate a message to them: software_coding_worker, software_coding_reviewer, software_coding_qa_worker, software_coding_manager \n"
                 "You should any individual src files you need to work with to code assistant context. \n"
                 "Note an agent cannot serve the purpose of a code assistant. \n"
                 "You should create or discover relevant assistants and use them otherwise upsert new ones. If creating a new one discover existing repositories or upsert new ones to associate to an assistant. \n"
                 "For software design and documentation you may leverage software_design_documentation_group prior to coding. \n"
                 "For independent code that may be reusable, the code output may be used to create functions for use within agents using the function_creation_group. \n"
                 "Uses code assistant via natural language to create code output."),
    agents_to_add=["software_coding_worker", "software_coding_reviewer", "software_coding_qa_worker", "software_coding_manager"],
    locked = True
)

functions_coding_group_model = UpsertGroupModel(
    name="function_creation_group",
    description="The Function Creation Group mirrors the structure of the Local and OpenAI Coding group but specializes in developing, testing, and refining reusable functions, ensuring they meet high standards of quality and efficiency. function_code_worker will create the function, function_checker will sanity check the function fields and test the function execution. function_checker will also transition the function from development to testing and finally to acceptance once accepted. function_manager will oversee the creation and testing process to ensure it goes smoothly. Use this group to make small functions and routines within a broader context to re-use in the future. Not meant for code applications end-to-end, just isolated routines. For applications, use coding_assistance_group. The following agents are in your group you can refer to them by name in your responses to communicate a message to them: function_code_worker, function_checker, function_manager",
    agents_to_add=["function_code_worker", "function_checker", "function_manager"],
    locked = True
)

zapier_group_model = UpsertGroupModel(
    name="zapier_automation_group",
    description="The Zapier Automation Group is dedicated to harnessing the power of APIs with almost infinite capabilities for seamless workflow automation and integration via Zapier. Zapier is an API aggregator that can solve almost any API task to external systems. It specializes in connecting a wide array of applications, facilitating data transfer, and automating tasks across platforms such as Google Workspace, Microsoft Office 365, Salesforce, Slack, Trello, Shopify, Mailchimp, Asana, QuickBooks, HubSpot, Dropbox, Airtable, Zendesk, WordPress, and Twitter. We focus on setting up and managing Zaps, ensuring robust API interactions, and optimizing processes for efficiency and reliability. Key activities include new actions (integrations), testing Zapier integrations, and customizing automation to align with specific workflow requirements. The following agents are in your group you can refer to them by name in your responses to communicate a message to them: zapier_api_manager, zapier_api_caller, zapier_api_tester",
    agents_to_add=["zapier_api_manager", "zapier_api_caller", "zapier_api_tester"],
    locked=True
)

external_group_models = [
    web_search_group_model,
    planning_group_model,
    software_coding_group_model,
    software_design_documentation_group_model,
    functions_coding_group_model,
    zapier_group_model
]
