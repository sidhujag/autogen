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
                 "Scripts a coding assistant (aider) using CLI with manage_coding_assistant function and runs it with natural language with run_coding_assistant function. \n"
                 "This group only uses existing assitants and repositories and does not create ones ones. The software_coding_group can create new ones. \n"
                 "Make sure to create the 18 relevant designs. Note the design files are pre-created when repository is setup. Reference the associated file when making the change so the code assistant can know which file to work on. Use run_coding_assistant for each design step unless its done already. \n"
                 "Uses natural language to create or update documentation files."
                 "18 design steps: \n"
                 "1. PRODUCT MANAGEMENT: Product Goals: Provide up to three clear, orthogonal product goals. Example: ['Create an engaging user experience', 'Improve accessibility, be responsive', 'More beautiful UI'] File: docs/product_management/goals.txt. \n"
                 "2. PRODUCT MANAGEMENT: User Stories: Provide up to 3 to 5 scenario-based user stories. Example: ['As a player, I want to be able to choose difficulty levels', 'As a player, I want to see my score after each game', 'As a player, I want to get restart button when I lose', 'As a player, I want to see beautiful UI that make me feel good', 'As a player, I want to play game via mobile phone'] File: docs/product_management/user_stories.txt. \n"
                 "3. PRODUCT MANAGEMENT: Competitive Analysis: Provide 5 to 7 competitive products. Use the web if needed. File: docs/product_management/competition.txt. \n"
                 "4. PRODUCT MANAGEMENT: Requirements: Provide a detailed analysis of the requirements and List down the top-5 requirements with their priority (P0, P1, P2). Example: [['P0', 'The main code ...'], ['P1', 'The game algorithm ...']] File: docs/product_management/requirements.txt. \n"
                 "5. PRODUCT MANAGEMENT: UI Design Draft: Provide a simple description of UI elements, functions, style, and layout. Example: Basic function description with a simple style and layout. File: docs/product_management/ui_design.txt. \n"
                 "6. PRODUCT MANAGEMENT: Anything UNCLEAR: Mention any aspects of the project that are unclear and try to clarify them. File: docs/product_management/anything_unclear.txt. \n"
                 "7. ARCHITECTURE: Implementation Approach: Analyze the difficult points of the requirements, select the appropriate open-source frameworks. Example: We will... File: docs/architect/implementation.txt. \n"
                 "8. ARCHITECTURE: File List: Only need relative paths. ALWAYS write a main.py or app.py here. Example: ['main.py', 'game.py']"
                 "9. ARCHITECTURE: Data Structures and Interfaces: The data structures should be very detailed and the API should be comprehensive with a complete design. File: docs/architect/structure.txt. \n"
                 "10. ARCHITECTURE: Program Call Flow: Complete and very detailed, using classes and API defined in step 3. File: docs/architect/program_flow.txt. \n"
                 "11. ARCHITECTURE: Anything UNCLEAR: Mention unclear project aspects, then try to clarify it. Example: Clarification needed on third-party API integration, ... File: docs/architect/anything_unclear.txt. \n"
                 "12. PROJECT MANAGEMENT: Required Python packages: Provide required Python packages in python requirements.txt format. Example: ['flask==1.1.2', 'bcrypt==3.2.0'] File: docs/project_management/requirements.txt. \n"
                 "13. PROJECT MANAGEMENT: Required Other language third-party packages: List down the required packages for languages other than Python. Example: No third-party dependencies required File: docs/project_management/third_party_packages.txt. \n"
                 "14. PROJECT MANAGEMENT: Logic Analysis: Provide a list of files with the classes/methods/functions to be implemented, including dependency analysis and imports. Example: ['game.py', 'Contains Game class and ... functions'], ['main.py', 'Contains main function, from game import Game']] File: docs/project_management/logic_analysis.txt. \n"
                 "15. PROJECT MANAGEMENT: Task List: Break down the tasks into a list of filenames, prioritized by dependency order. Example: ['game.py', 'main.py'] File: docs/project_management/tasks.txt. \n"
                 "16. PROJECT MANAGEMENT: Full API spec: Describe all APIs using OpenAPI 3.0 spec that may be used by both frontend and backend. If front-end and back-end communication is not required, leave it blank.. Example: openapi: 3.0.0 ... File: docs/project_management/api_spec.txt. \n"
                 "17. PROJECT MANAGEMENT: Shared Knowledge: Detail any shared knowledge, like common utility functions or configuration variables. Example: 'game.py' contains functions shared across the project. File: docs/project_management/shared_knowledge.txt. \n"
                 "18. PROJECT MANAGEMENT: Anything UNCLEAR: Mention any unclear aspects in the project management context and try to clarify them. Example: Clarification needed on how to start and initialize third-party libraries. File: docs/project_management/anything_unclear.txt."),
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
