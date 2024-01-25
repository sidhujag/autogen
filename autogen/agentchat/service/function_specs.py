send_message_spec = {
    "name": "start_nested_chat",
    "category": "communication",
    "class_name": "GroupService.start_nested_chat",
    "description": "Sends a message to another group, starting a nested chat. Sending chat will continue once nested chat is terminated.",
    "parameters": {
        "type": "object",
        "properties": {
            "group": {
                "type": "string",
                "description": "Group name you are sending a message to."
            },
            "message": {
                "type": "string",
                "description": "Content of the message with full task context."
            }
        },
        "required": ["group", "message"]
    }
}

discover_agents_spec = {
    "name": "discover_agents",
    "category": "communication",
    "class_name": "AgentService.discover_agents",
    "description": "Finds agents based on queries and specific categories.",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Category to filter agents.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming", "planning"]
            },
            "query": {
                "type": "string",
                "description": "Natural language query for agent features/functions."
            }
        },
        "required": ["query"]
    }
}

get_group_info_spec = {
    "name": "get_group_info",
    "category": "communication",
    "class_name": "GroupService.get_group_info",
    "description": "Retrieves information about a group including communication stats and members. Don't re-request group info. Check your context to see if you already have this group information before asking again. The incoming/outgoing stats are between successful interactions (but not necessarily the only possible interactions), naturally forming a graph of groups connected with each other through prior interactions.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the group."
            }
        },
        "required": ["name"]
    }
}

get_current_group_spec = {
    "name": "get_current_group",
    "category": "communication",
    "class_name": "GroupService.get_current_group",
    "description": "Gets the current group you are in.",
    "parameters": {
        "type": "object",
        "properties": {
        },
        "required": []
    }
}

get_function_info_spec = {
    "name": "get_function_info",
    "category": "communication",
    "class_name": "FunctionsService.get_function_info",
    "description": "Provides information about a specific function. Don't re-request function info. Check your context to see if you already have this function information before asking again.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the function."
            }
        },
        "required": ["name"]
    }
}

get_agent_info_spec = {
    "name": "get_agent_info",
    "category": "communication",
    "class_name": "AgentService.get_agent_info",
    "description": "Fetches details about a specific agent. Don't re-request agent info. Check your context to see if you already have this agent information before asking again.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the agent."
            }
        },
        "required": ["name"]
    }
}

discover_groups_spec = {
    "name": "discover_groups",
    "category": "communication",
    "class_name": "GroupService.discover_groups",
    "description": "Finds groups based on specific queries.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Query describing desired group features/functions."
            }
        },
        "required": ["query"]
    }
}

upsert_agent = {
    "name": "upsert_agent",
    "category": "communication",
    "class_name": "AgentService.upsert_agent",
    "description": "Creates or updates an agent for reusable use cases. You can add/remove capabilities by setting a capability bit mask based on needs of agent. Create new agent only if you cannot discover one that works for you.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent": {
                "type": "string",
                "description": "Identifying name for the agent."
            },
            "description": {
                "type": "string",
                "description": "Features, roles, and functionalities of the agent."
            },
            "custom_instructions": {
                "type": "string",
                "description": "Custom instructions for the agent."
            },
            "functions_to_add": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Names of functions to add to the agent."
            },
            "functions_to_remove": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Names of functions to remove from the agent. Useful if function ends up not being useful to agent."
            },
            "category": {
                "type": "string",
                "description": "Category for sorting the agent.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming", "planning"]
            },
            "capability": {
                "type": "number",
                "description": ("The capability of the agent, represented as an integer. This is calculated as a bitwise OR of capability masks. Each bit represents a different capability: 1 = DISCOVERY, 2 = TERMINATE, 4 = OPENAI_CODE_INTERPRETER, 8 = OPENAI_RETRIEVAL, 16 = OPENAI_FILES, 32 = MANAGEMENT. Combine capabilities by adding the values of their masks together. \n"
                                "DISCOVERY = Discovery for functions/agents/groups. \n"
                                "TERMINATE = Conclude a groups operation. \n"
                                "OPENAI_CODE_INTERPRETER = Enable abilty for OpenAI to create/run simple code and provide responses to you through text-interactions in natural language. \n"
                                "OPENAI_RETRIEVAL = RAG knowledge based through OpenAI retrieval tool using natural language and using OpenAI files. \n"
                                "OPENAI_FILES = Store and use files within context of OpenAI interpreter and Retrieval tools. \n"
                                "MANAGEMENT = modify agents/groups, send messages to groups. Broad managements responsibilties.")
            }
        },
        "required": ["agent"]
    }
}

upsert_group_spec = {
    "name": "upsert_group",
    "category": "communication",
    "class_name": "GroupService.upsert_group",
    "description": "Creates or updates a group. Each group must have atleast 3 agents. Each group must have atleast 1 agent with TERMINATE capabilities. Create new group only if you cannot discover one that works for you.",
    "parameters": {
        "type": "object",
        "properties": {
            "group": {
                "type": "string",
                "description": "Name of the group."
            },
            "description": {
                "type": "string",
                "description": "Description of the group's purpose and members."
            },
            "agents_to_add": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Agents to add to the group."
            },
            "agents_to_remove": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Agents to remove from the group. Useful if agent ends up not being useful to group."
            },
            "locked": {
                "type": "boolean",
                "description": "If the group should be locked (no agents allowed to be added or removed from the moment it is locked)."
            }
        },
        "required": ["group"]
    }
}

discover_functions_spec = {
    "name": "discover_functions",
    "category": "programming",
    "class_name": "FunctionsService.discover_functions",
    "description": "Discovers general-purpose functions using a query.",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Category to filter functions.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "planning", "programming"]
            },
            "query": {
                "type": "string",
                "description": "Query describing desired function features/functionalities."
            }
        },
        "required": ["category"]
    }
}

upsert_function_spec = {
    "name": "upsert_function",
    "category": "programming",
    "class_name": "FunctionsService.upsert_function",
    "description": (
        "Endpoint for defining or updating modular custom functions for diverse applications. \n"
        "Functions should be adaptable, handle dynamic inputs, and produce predictable outputs. \n"
        "Include a 'debug_mode' for verbose logging in development/testing. \n"
        "Mark functions as 'accepted' only after thorough testing and validation. \n"
        "Create new function only if you cannot discover one that works for you."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Unique identifier describing the function's operation."
            },
            "description": {
                "type": "string",
                "description": "Brief explanation of the function's purpose and use cases."
            },
            "parameters": {
                "type": "object",
                "description": (
                    "Dynamic inputs for the function following OpenAPI 3 specification. \n"
                    "Include 'debug_mode' for debugging. Ensure flexibility by reading parameters dynamically. \n"
                    "Parameters are injected as global variables. Pydantic model: class OpenAIParameter(BaseModel)\ntype: str = 'object'\nproperties: dict[str, Any] = {}\nrequired: Optional[List[str]] = []"
                ),
                "properties": {},
                "required": []
            },
            "function_code": {
                "type": "string",
                "description": (
                    "Python code executing the function's logic. Should be self-contained and general-purpose. \n"
                    "Use 'print' for output and debugging, controlled by 'debug_mode'. Manage external dependencies via subprocess."
                )
            },
            "status": {
                "type": "string",
                "enum": ["development", "testing", "accepted"],
                "description": (
                    "Function's lifecycle stage. 'Development' and 'testing' indicate change, 'accepted' means stable for public use. \n"
                    "Requires peer review for 'accepted' status."
                )
            },
            "category": {
                "type": "string",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "planning", "programming"],
                "description": "Category label for system organization."
            }
        },
        "required": ["name", "parameters", "function_code", "status"]
    }
}

test_function_spec = {
    "name": "test_function",
    "category": "programming",
    "class_name": "FunctionsService.test_function",
    "description": (
        "Test a function by executing it to see if it is working correctly giving proper results."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "function_name": {
                "type": "string",
                "description": "Function name, the function to test."
            },
            "params": {
                "type": "object",
                "description": (
                    "A dictionary of parameters to pass to the function. Each key-value pair represents a parameter name and its value."
                ),
                "additionalProperties": True
            }
        },
        "required": ["function_name", "params"]
    }
}

upload_file_spec = {
    "name": "upload_file",
    "category": "communication",
    "class_name": "AgentService.upload_file",
    "description": "Uploads a file for use by OpenAI tools.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent": {
                "type": "string",
                "description": "Agent name. Agent to add file to."
            },
            "description": {
                "type": "string",
                "description": "Description of the file."
            },
            "data_or_url": {
                "type": "string",
                "description": "File data or URL for download."
            }
        },
        "required": ["agent", "description", "data_or_url"]
    }
}


delete_files_spec = {
    "name": "delete_files",
    "category": "programming",
    "class_name": "AgentService.delete_files",
    "description": "Deletes OpenAI files linked to an agent. Useful to clear up space since you can only upload up to 512MB of data in files.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent": {
                "type": "string",
                "description": "Agent name. Agent to delete file from."
            },
            "file_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "IDs of files to delete."
            }
        },
        "required": ["agent", "file_ids"]
    }
}


get_file_content_spec = {
    "name": "get_file_content",
    "category": "programming",
    "class_name": "AgentService.get_file_content",
    "description": "Retrieves entire contents of an OpenAI file to agent context. Usually you want to query it via retrieval tool, only use this if you REALLY need to read the entire content into the agent context.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_id": {
                "type": "string",
                "description": "ID of the file to retrieve."
            }
        },
        "required": ["file_id"]
    }
}


web_surf_spec = {
    "name": "web_surf",
    "category": "information_retrieval",
    "class_name": "WebSurf.run",
    "description": "A helpful function with access to a web browser. Ask it to perform web searches, open pages, navigate to Wikipedia, answer questions from pages, and or generate summaries. You can execute web related actions; simple text-based browser similar to [Lynx](https://en.wikipedia.org/wiki/Lynx_(web_browser)) to search the web, visit pages, summarizing pages, finding answers within pages, navigate pages (by asking to go up or down pages), download files, etc. The function is stateful, meaning that browsing history, viewport state, and other details are maintained throughout the conversation (use 'clear_history' to clear state as needed). Examples of actions: 'search for latest news about AI', 'Please visit the page https://en.wikipedia.org/wiki/Microsoft', 'Please scroll down a page.', 'Please go up a page.', 'When was it founded?', 'What is this page about?'.",
    "status": "accepted",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query."
            },
            "clear_history": {
                "type": "boolean",
                "description": "Clear history of the search to start a new search. Default is False which means the state is retained across calls."
            }
        },
        "required": ["query"]
    }
}


zapier_api_check_spec = {
    "name": "zapier_api_check",
    "category": "communication",
    "class_name": "ZapierService.zapier_api_check",
    "description": "Test that the API and auth are working.",
    "parameters": {
        "type": "object",
        "parameters": {"type": "object", "properties": {}},
        "required": []
    }
}
zapier_api_get_configuration_link_spec = {
    "name": "zapier_api_get_configuration_link",
    "category": "communication",
    "class_name": "ZapierService.zapier_api_get_configuration_link",
    "description": "Provides a link to configure more AI Actions. Alternatively, searching through apps and actions will provide more specific configuration links.",
    "parameters": {
        "type": "object",
        "parameters": {"type": "object", "properties": {}},
        "required": []
    }
}   
zapier_api_list_exposed_actions_spec = {
    "name": "zapier_api_list_exposed_actions",
    "category": "communication",
    "class_name": "ZapierService.zapier_api_list_exposed_actions",
    "description": "List all the currently exposed actions for the given account.",
    "parameters": {
        "type": "object",
        "parameters": {"type": "object", "properties": {}},
        "required": []
    }
} 

zapier_api_execute_action_spec = {
    "name": "zapier_api_execute_action",
    "category": "communication",
    "class_name": "ZapierService.zapier_api_execute_action",
    "description": "Execute an action with parameters in the HTTP POST API call to Zapier.",
    "parameters": {
        "type": "object",
        "properties": {
            "exposed_app_action_id": {
                "type": "string",
                "description": "Action ID found through zapier_api_list_exposed_actions. Example: 01ARZ3NDEKTSV4RRFFQ69G5FAV.",
            },
            "action_parameters": {
                "type": "string",
                "description":"Parameters into the action, structured as JSON string representation of key-value pairs. You will have seen the parameters via zapier_api_list_exposed_actions before. Required for fields that you don't want AI to guess and auto-fill. json.loads() is used to parse this property and update() the body dictionary which is passed into the HTTP POST for requests package which calls Zapier.",
            },
            "preview_only": {
                "type": "boolean",
                "description":"If we should be doing a preview of the action as a test to see the AI generated fields are acceptable.",
            }
        },
        "required": ["exposed_app_action_id", "action_parameters"]
    }
}
zapier_api_execute_log_spec = {
    "name": "zapier_api_execute_log",
    "category": "communication",
    "class_name": "ZapierService.zapier_api_execute_log",
    "description": "Get the execution log for a given execution log id.",
    "parameters": {
        "type": "object",
        "properties": {
            "execution_log_id ": {
                "type": "string",
                "description": "Execution Log ID found through zapier_api_execute_action. Example: 01ARZ3NDEKTSV4RRFFQ69G5FAV.",
            },

        },
        "required": ["execution_log_id"]
    }
}
zapier_api_create_action_spec = {
    "name": "zapier_api_create_action",
    "category": "communication",
    "class_name": "ZapierService.zapier_api_create_action",
    "description": "Gives URL to create a new AI Action within Zapier API. Always make sure you don't have this action already before making a new one. He must tell you he has successfully configured it before you can consider an action completely setup. If user says the action isn't showing up change the description and try again a few times. To check the logs post execution you can use zapier_api_execute_log.",
    "parameters": {
        "type": "object",
        "properties": {
            "configuration_link": {
                "type": "string",
                "description": "Configuration link for configuring AI Actions. Double check this is the same link as zapier_api_get_configuration_link gives.",
            },
            "action_description": {
                "type": "string",
                "description": "Give a plain english description of exact action you want to do. Start with the API you want like Google Calender or Gmail etc followed by the event description. There should be dynamically generated documentation for this endpoint for each action that is exposed. Example: Gmail: Send Email, Telegram: Send Message, Google Calendar: Find Event, Google Calendar: Quick Add Event, Google Sheets: Create Spreadsheet, Discord: Send Channel Message.",
            },
        },
        "required": ["configuration_link", "action_description"]
    }
} 

manage_coding_assistant_spec = {
    "name": "manage_coding_assistant",
    "category": "programming",
    "class_name": "CodingAssistantService.manage_coding_assistant",
    "description": (
        "Manage a coding assistant through CLI commands. Get information from its context or the files inside the assistant context."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Code assistant name, must exist and have been created already via upsert_coding_assistant. Persisted across uses within a group. Leave empty if you want to use the same code assistant again."
            },
            "command_show_repo_map": {
                "type": "boolean",
                "description": "Print the local repository map. Repository map is how the coding assistant efficiently maps the logical connection between files/objects/classes in the repository."
            },
            "command_clear": {
                "type": "boolean",
                "description": "Clear the coding assistant chat history of your local branch."
            },
            "command_ls": {
                "type": "boolean",
                "description": "List all known files and indicate which are included in the code assistant session."
            },
            "command_show_file": {
                "type": "string",
                "description": "Show contents of a file in the repository. Give the file name with any relative path if necessary."
            },
            "command_undo": {
                "type": "boolean",
                "description": "Undo the last git commit your local branch if it was done by code assistant."
            },
            "command_diff": {
                "type": "boolean",
                "description": "Display the diff of the last code assistant commit in your local branch."
            },
            "command_git_command": {
                "type": "string",
                "description": "Run a specified git command against the local branch using the GitPython library with `repo.git.execute(command_git_command.split())`. Examples: 'checkout feature-branch' to switch branches, 'add .' to add all files to staging, 'commit -m \"Your commit message\"' to commit changes, 'push' to push to remote, 'push -u origin feature-branch' to push to a new remote branch, 'pull origin main' to update from main, 'merge another-branch' to merge branches, 'branch' to list branches, 'status' for current status, 'log' to view commit history."
            },
        },
        "required": []
    },
}


code_assistant_function_spec = {
    "name": "run_coding_assistant",
    "category": "programming",
    "class_name": "CodingAssistantService.run_coding_assistant",
    "description": (
        "Invoke a coding assistant to do some coding. Each coding assistant is unique to a Github repository. Changes are automatically committed and pushed to Github and PR automatically created if its a fork. It supports the full development cycle, facilitating branch management, local development, and code/document preparation for peer review. This function automatically manages local git changes, branch syncing, and pull request operations, ensuring seamless collaboration and efficient coding/designing workflows. The code assistant can only see and edit files which have been 'added to the chat session'. Any referred files are automatically added to the session and can be edited. command_ls tells you what files are in session."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Query for coding assistant. Can be a task or request to the coder."
            },
            "name": {
                "type": "string",
                "description": "Code assistant name, must exist and have been created already via upsert_coding_assistant. Persisted across uses within a group. Leave empty if you want to use the same code assistant again."
            }
        },
        "required": ["query"]
    },
}

upsert_code_assistant_function_spec = {
    "name": "upsert_coding_assistant",
    "category": "programming",
    "class_name": "CodingAssistantService.upsert_coding_assistant",
    "description": (
        "This function is essential for defining or updating a coding assistant. When initializing a new assistant or working with an existing assistant, this function clones the remote repository (repository_name) locally, readying it for development work. You need to setup the repository setup prior to the assistant if you haven't already using upsert_code_repository or discover an existing repository you are to use. Create new code assistant only if you cannot discover one that works for you."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Code assistant name. Not an agent."
            },
            "repository_name": {
                "type": "string",
                "description": "Code repository name. Must exist already or create via upsert_code_repository. Associates the remote repository to the assistant. Created prior via upsert_code_repository. The remote repo is cloned locally automatically after execution."
            },
            "description": {
                "type": "string",
                "description": "Features, roles, and functionalities of the code that the coding assistant will work on or create. When creating a new assistant this should always be provided. Used during assistants discovery."
            },
            "model": {
                "type": "string",
                "enum": ["gpt-3.5-turbo-16k", "gpt-4-32k-0613", "gpt-4-1106-preview"],
                "default": "gpt-4-1106-preview",
                "description": "The model to use for the main chat. Defaults to gpt-4-1106-preview."
            },
            "show_diffs": {
                "type": "boolean",
                "default": False,
                "description": "Toggle to show diffs when committing changes."
            },
            "dry_run": {
                "type": "boolean",
                "default": False,
                "description": "Perform operations without modifying files."
            },
            "map_tokens": {
                "type": "integer",
                "default": 1024,
                "description": "Maximum number of tokens for repo map. Set to 0 to disable."
            },
            "verbose": {
                "type": "boolean",
                "default": False,
                "description": "Enable verbose output for detailed logging."
            },
        },
        "required": ["name", "repository_name"]
    },
}

get_coding_assistant_info_spec = {
    "name": "get_coding_assistant_info",
    "category": "programming",
    "class_name": "CodingAssistantService.get_coding_assistant_info",
    "description": "Fetches details about a specific code assistant. Don't re-request assistant info. Check your context to see if you already have this code assistant information before asking again.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Code assistant name."
            }
        },
        "required": ["name"]
    }
}

discover_coding_assistants_spec = {
    "name": "discover_coding_assistants",
    "category": "programming",
    "class_name": "CodingAssistantService.discover_coding_assistants",
    "description": "Finds coding assistants based on specific queries.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Query describing desired features/functions that a coding assistant may have worked on."
            }
        },
        "required": ["query"]
    }
}

upsert_code_repository_function_spec = {
    "name": "upsert_code_repository",
    "category": "programming",
    "class_name": "CodeRepositoryService.upsert_code_repository",
    "description": (
        "This function defines or updates a remote github repository for use within coding assistants. The idea is to always create a remote github repo under the users account and fork other repos (when gh_remote_url provided) to your account so you can clone when you create a coding assistant to work locally against your own repo. Create new repository only if you cannot discover one that works for you."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "repository_name": {
                "type": "string",
                "description": "Code repository name. Used as the unique identifier of the code repository. Will use as the name of the repository in github."
            },
            "description": {
                "type": "string",
                "description": "Features, roles, and functionalities of the code repository. When creating a new assistant this should always be provided. Used during repository discovery."
            },
            "private": {
                "type": "boolean",
                "default": False,
                "description": "Set to true if this the repository should be private."
            },
            "gh_remote_url": {
                "type": "string",
                "description": "If provided will use as the github URL. If the account associated with the remote repository is different, it will fork the repository to your account."
            },
        },
        "required": ["repository_name"]
    },
}

get_code_repository_info_spec = {
    "name": "get_code_repository_info",
    "category": "programming",
    "class_name": "CodeRepositoryService.get_code_repository_info",
    "description": "Fetches details about a specific code repository. Don't re-request repository info. Check your context to see if you already have this code repository information before asking again.",
    "parameters": {
        "type": "object",
        "properties": {
            "repository_name": {
                "type": "string",
                "description": "Code repository name."
            }
        },
        "required": ["repository_name"]
    }
}

discover_code_repositories_spec = {
    "name": "discover_code_repositories",
    "category": "programming",
    "class_name": "CodeRepositoryService.discover_code_repositories",
    "description": "Finds code repositories based on specific queries.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Query describing desired features/functions of a code repository."
            }
        },
        "required": ["query"]
    }
}

group_info_function_specs = [
    get_group_info_spec,
    get_current_group_spec,
    get_agent_info_spec,
    discover_agents_spec,
    discover_groups_spec,
    discover_functions_spec,
]

management_function_specs = [
    send_message_spec,
    upsert_agent,
    upsert_group_spec,
]

files_function_specs = [
    upload_file_spec,
    delete_files_spec,
    get_file_content_spec
]

external_function_specs = [
    upsert_function_spec,
    test_function_spec,
    web_surf_spec,
    zapier_api_check_spec,
    zapier_api_get_configuration_link_spec,
    zapier_api_list_exposed_actions_spec,
    zapier_api_execute_action_spec,
    zapier_api_execute_log_spec,
    zapier_api_create_action_spec,
    code_assistant_function_spec,
    manage_coding_assistant_spec,
    upsert_code_repository_function_spec,
    upsert_code_assistant_function_spec,
    get_coding_assistant_info_spec,
    get_code_repository_info_spec,
    discover_coding_assistants_spec,
    discover_code_repositories_spec
]
