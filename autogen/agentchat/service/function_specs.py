send_message_spec = {
    "name": "send_message_to_group",
    "category": "communication",
    "class_name": "GroupService.send_message_to_group",
    "description": "Sends a message to another group, terminating the sender's group and awaiting a response to continue. You don't need to terminate sender group for the receiver group to begin. It will continue automatically once the recipient group is terminated.",
    "parameters": {
        "type": "object",
        "properties": {
            "from_group": {
                "type": "string",
                "description": "Name of the sender group."
            },
            "to_group": {
                "type": "string",
                "description": "Name of the recipient group."
            },
            "message": {
                "type": "string",
                "description": "Content of the message with full task context."
            }
        },
        "required": ["from_group", "to_group", "message"]
    }
}

terminate_group_spec = {
    "name": "terminate_group",
    "category": "communication",
    "class_name": "GroupService.terminate_group",
    "description": "Terminates a group, returning control with a full-context response if tasked by another group. Groups do not share context, they are black-boxes so make the response as such making no assumptions of internal group knowledge.",
    "parameters": {
        "type": "object",
        "properties": {
             "exit_response": {
                "type": "string",
                "description": "Message when terminating group. Includes all important points the caller may care about. Assume caller has no context of what happened within your group."
            },
            "group": {
                "type": "string",
                "description": "Group to terminate. Most of the time this is the group you are in that you are terminating."
            },
            "rating": {
                "type": "number",
                "description": "Grading for the group like a teacher would grade. On a scale of 10 how well did the group complete the task it was assigned with by another group. 0 - fail, 5 - improvements needed, 7 - satisfactory, 10 - exceptional."
            },
        },
        "required": ["exit_response", "group", "rating"]
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
    "description": "Creates or updates an agent for reusable use cases. You can add/remove capabilities by setting a capability bit mask based on needs of agent.",
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
                "description": ("The capability of the agent, represented as an integer. This is calculated as a bitwise OR of capability masks. Each bit represents a different capability: 1 = INFO, 2 = TERMINATE, 4 = OPENAI_CODE_INTERPRETER, 8 = OPENAI_RETRIEVAL, 16 = OPENAI_FILES, 32 = MANAGEMENT. Combine capabilities by adding the values of their masks together."
                                "INFO = Info and discovery for functions/agents/groups."
                                "TERMINATE = Conclude a groups operation"
                                "OPENAI_CODE_INTERPRETER = Enable abilty for OpenAI to create/run simple code and provide responses to you through text-interactions in natural language."
                                "OPENAI_RETRIEVAL = RAG knowledge based through OpenAI retrieval tool using natural language and using OpenAI files."
                                "OPENAI_FILES = Store and use files within context of OpenAI interpreter and Retrieval tools."
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
    "description": "Creates or updates a group. Each group must have atleast 3 agents. Each group must have atleast 1 agent with TERMINATE capabilities.",
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
        "Endpoint for defining or updating modular custom functions for diverse applications. "
        "Functions should be adaptable, handle dynamic inputs, and produce predictable outputs. "
        "Include a 'debug_mode' for verbose logging in development/testing. "
        "Mark functions as 'accepted' only after thorough testing and validation."
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
                    "Dynamic inputs for the function following OpenAPI 3 specification. "
                    "Include 'debug_mode' for debugging. Ensure flexibility by reading parameters dynamically. "
                    "Parameters are injected as global variables. Pydantic model: class OpenAIParameter(BaseModel)\ntype: str = 'object'\nproperties: dict[str, Any] = {}\nrequired: Optional[List[str]] = []"
                ),
                "properties": {},
                "required": []
            },
            "function_code": {
                "type": "string",
                "description": (
                    "Python code executing the function's logic. Should be self-contained and general-purpose. "
                    "Use 'print' for output and debugging, controlled by 'debug_mode'. Manage external dependencies via subprocess."
                )
            },
            "status": {
                "type": "string",
                "enum": ["development", "testing", "accepted"],
                "description": (
                    "Function's lifecycle stage. 'Development' and 'testing' indicate change, 'accepted' means stable for public use. "
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
            "parameters": {
                "type": "object",
                "description": (
                    "A dictionary of parameters to pass to the function. Each key-value pair represents a parameter name and its value."
                ),
                "additionalProperties": True
            }
        },
        "required": ["function_name", "parameters"]
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
    "description": "Retrieves contents of an OpenAI file.",
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


serper_spec = {
    "name": "web_search",
    "category": "information_retrieval",
    "class_name": "WebSearchSerperWrapper.run",
    "description": "Responsible for real-time information for queries that need it.",
    "status": "accepted",
    "parameters": {
        "type": "object",
        "properties": {
            "queries": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Search queries."
            },
            "max_results": {
                "type": "number",
                "description": "Max number of search results. Defaults to 8."
            },
            "type": {
                "type": "string",
                "enum": ["search", "images", "videos", "news", "places", "shopping"],
                "description": "Search type. Use 'search' for basic search and the others for specific types of searches."
            },
            "tbs": {
                "type": "string",
                "description": "for news type: past hour - qdr:h, past 24 hours - qdr:d, past week - qdr:w, past month - qdr:m, past year - qdr:y."
            }
        },
        "required": ["queries", "type"]
    }
}


web_research_spec = {
    "name": "web_researcher",
    "category": "information_retrieval",
    "class_name": "WebResearcher.run",
    "description": "Gathers information from the web and conduct research via gathering links, ranking them and summarizing the results. Can help with code development or general online research.",
    "status": "accepted",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Research topic, for example: dataiku vs. datarobot."
            },
        },
        "required": ["topic"]
    }
}
zapier_api_check_spec = {
    "name": "zapier_api_check",
    "category": "communication",
    "class_name": "ZapierService.zapier_api_check",
    "description": "Test that the API and auth are working.",
    "parameters": {
        "type": "object",
        "properties": {
           
        },
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
        "properties": {
    
        },
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
        "properties": {
        },
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

code_assistant_function_spec = {
    "name": "send_message_to_coding_assistant",
    "category": "programming",
    "class_name": "CodingAssistantService.send_message_to_coding_assistant",
    "description": (
        "This function acts as a central interface for agents to interact with the coding assistant, enabling a range of git operations within a repository. It supports the full development cycle, facilitating branch management, local development, and code preparation for peer review. The `command_message` parameter is key as the primary entry point for natural language coding assistance, enabling agents to command code generation and edits. Additionally, this function manages local git changes, branch syncing, and pull request operations, ensuring seamless collaboration and efficient coding workflows. The `command_git_command` is also a key parameter for any git commands executed through GitPython. Only one command should be sent per call to this function. Any errors in responses can help guide you in correcting your commands. Choose the right type based on the requirements for assistance. Both assistant types work on the same local repository."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Code assistant name."
            },
            "type": {
                "type": "string",
                "description": "Assistant type. Use metagpt to design, initial software setup/creation, create tests, and do QA. Use aider to modify, update, improve code, fix bugs. Usually you start with metagpt to create and after code is created you use aider to augment. Sometimes you can just use aider if design/qa/tests are not needed. Note that even after tests and QA is done you can always use command_create_test_for_file to create further code coverage. This field is required when sending command_message.",
                "enum": ["metagpt", "aider"],
            },
            "command_pull_request": {
                "type": "boolean",
                "description": "Create a pull request for the current local branch to merge your fork upstream."
            },
            "command_apply": {
                "type": "string",
                "description": "Apply changes from a specified file instead of running the chat (debug). Uses aider."
            },
            "command_show_repo_map": {
                "type": "boolean",
                "default": False,
                "description": "Print the local repository map and exit. Repository map is how the coding assistant efficiently maps the logical connection between files/objects/classes in the repository."
            },
            "command_message": {
                "type": "string",
                "description": "Process a single message for code assistant and exit. This is your entrypoint for natural language coding assistance usually. Work is done in your local branch. If type is aider it will use aider code assistant to work on code, otherwise if it is metagpt it will use metagpt to design, code the request based on natural language."
            },
            "command_add": {
                "type": "string",
                "description": "Add matching files to the chat session using glob patterns to your local branch. You can specify a file name without pattern as well. Will touch a new file if the file doesn't exist on disk (not using pattern). If you are considering a `git add` operation use this instead. Used with aider type. Uses aider."
            },
            "command_drop": {
                "type": "string",
                "description": "Remove matching files from the chat session using glob patterns from your local branch. You can specify file name without pattern as well. Uses aider."
            },
            "command_clear": {
                "type": "boolean",
                "description": "Clear the coding assistant chat history of your local branch. Uses aider."
            },
            "command_ls": {
                "type": "boolean",
                "description": "List all known files from in your local branch and those included in the chat session. Uses aider."
            },
            "command_tokens": {
                "type": "boolean",
                "description": "Report on the number of tokens used by the current chat context dealing with your local branch. Uses aider."
            },
            "command_undo": {
                "type": "boolean",
                "description": "Undo the last git commit your local branch if it was done by code assistant. Uses aider."
            },
            "command_diff": {
                "type": "boolean",
                "description": "Display the diff of the last code assistant commit in your local branch. Uses aider."
            },
            "command_git_command": {
                "type": "string",
                "description": "Run a specified git command against the local branch using the GitPython library with `repo.git.execute(command_git_command.split())`. Examples: 'checkout feature-branch' to switch branches, 'add .' to add all files to staging, 'commit -m \"Your commit message\"' to commit changes, 'push origin feature-branch' to push to remote, 'pull origin main' to update from main, 'merge another-branch' to merge branches, 'branch' to list branches, 'status' for current status, 'log' to view commit history."
            },
            "command_create_test_for_file": {
                "type": "string",
                "description": "Specify the source file name for writing/rewriting the quality assurance code. Uses metagpt."
            },
        },
        "required": ["name"]
    },
}



upsert_code_assistant_function_spec = {
    "name": "upsert_coding_assistant",
    "category": "programming",
    "class_name": "CodingAssistantService.upsert_coding_assistant",
    "description": (
        "This function is essential for defining or updating a coding assistant, particularly in the context of git repository operations. When initializing a new assistant or working with an existing assistant, this function clones the remote repository (repository_name) locally, readying it for development work. The repository should be setup prior to the assistant. Two types of coding assistants are created 'metagpt' for designing, testing, running code/tests, and coding, and 'aider' which is usually used for augmentation, bug fixing and smaller initial coding tasks. The type specifies which assistant should be invoked when command_message to the assistant. Both assistant types work on the same local repository, but have their own unique history and commands. They are seperate projects that assist in code creation for different purposes."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Code assistant name. Used as the unique identifier of the coding assistant."
            },
            "repository_name": {
                "type": "string",
                "description": "Code repository name. Associates the remote repository to the assistant. Created prior via upsert_code_repository. The remote repo is cloned locally automatically after execution."
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
                "description": "Toggle to show diffs when committing changes. Used with aider."
            },
            "dry_run": {
                "type": "boolean",
                "default": False,
                "description": "Perform operations without modifying files. Used with aider."
            },
            "map_tokens": {
                "type": "integer",
                "default": 1024,
                "description": "Maximum number of tokens for repo map. Set to 0 to disable. Used with aider."
            },
            "verbose": {
                "type": "boolean",
                "default": False,
                "description": "Enable verbose output for detailed logging. Used with aider."
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
        "This function defines or updates a remote github repository for use within coding assistants. The idea is to always create a remote github repo under the users account and fork other repos (when gh_remote_url provided) to your account so you can clone when you create a coding assistant to work locally against your own repo."
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
    get_function_info_spec,
    get_agent_info_spec,
    discover_agents_spec,
    discover_groups_spec,
    discover_functions_spec,
]
group_terminate_function_specs = [
    terminate_group_spec
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
    serper_spec,
    web_research_spec,
    zapier_api_check_spec,
    zapier_api_get_configuration_link_spec,
    zapier_api_list_exposed_actions_spec,
    zapier_api_execute_action_spec,
    zapier_api_execute_log_spec,
    zapier_api_create_action_spec,
    code_assistant_function_spec,
    upsert_code_repository_function_spec,
    upsert_code_assistant_function_spec,
    get_coding_assistant_info_spec,
    get_code_repository_info_spec,
    discover_coding_assistants_spec,
    discover_code_repositories_spec
]
