send_message_spec = {
    "name": "send_message_to_group",
    "category": "communication",
    "class_name": "GroupService.send_message_to_group",
    "description": "Send a message to another group to assign a task. When you send a message to another group your current group will terminate and upon termination of the recipient group a response will be sent back to you so your group can continue. Before sending check that the recipient is a valid existing group, has 3 or more agents inside it with atleast 1 being from MANAGEMENT.",
    "parameters": {
        "type": "object",
        "properties": {
            "from_group": {"type": "string", "description": "The name of the sending group you are sending message from."},
            "to_group": {"type": "string", "description": "The name of the recipient group."},
            "message": {"type": "string", "description": "The content of the message. In the message you should include full context of what your task is for the recipient group because the recipient group does not share message history with your group."},
        },
        "required": ["from_group", "to_group", "message"]
    }
}

terminate_group_spec = {
    "name": "terminate_group",
    "category": "communication",
    "class_name": "GroupService.terminate_group",
    "description": "Terminate and conclude a group. The groupchat has a loop that continues to select a next speaker until it is terminated. If you have been sent a task by another group, this will give control back with a response.",
    "parameters": {
        "type": "object",
        "properties": {
            "group": {"type": "string", "description": "The group you are terminating."},
            "response": {"type": "string", "description": "Summary of group discussion and response back to the dependent group if there is one."},
        },
        "required": ["group", "response"]
    }
}

discover_agents_spec = {
    "name": "discover_agents",
    "category": "communication",
    "class_name": "AgentService.discover_agents",
    "description": "Discover other agents based on specific queries.",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "A category to filter agents based on predefined categories. 'user' category is for different agents that allow communication with the user.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming", "planning", "user"]
            },
            "query": {
                "type": "string",
                "description": "A natural language query describing the desired features, functions, or functionalities of the agent being searched for."
            }
        },
        "required": ["query"]
    },
}

get_group_info_spec = {
    "name": "get_group_info",
    "category": "communication",
    "class_name": "GroupService.get_group_info",
    "description": "Get group info by name: Communication stats of the group as well as agents/files in group.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The group name."
            }
        },
        "required": ["name"]
    },
}

get_function_info_spec = {
    "name": "get_function_info",
    "category": "communication",
    "class_name": "FunctionsService.get_function_info",
    "description": "Get function info ny name.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The function name."
            }
        },
        "required": ["name"]
    },
}

get_agent_info_spec = {
    "name": "get_agent_info",
    "category": "communication",
    "class_name": "AgentService.get_agent_info",
    "description": "Get agent info by name.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The agent name."
            }
        },
        "required": ["name"]
    },
}

discover_groups_spec = {
    "name": "discover_groups",
    "category": "communication",
    "class_name": "GroupService.discover_groups",
    "description": "Discover groups based on specific queries.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A natural language query describing the desired features, functions, or functionalities of the group being searched for."
            }
        },
        "required": ["query"]
    },
}

upsert_agent = {
    "name": "upsert_agent",
    "category": "communication",
    "class_name": "AgentService.upsert_agent",
    "description": "Upsert an agent. Create an agent only for reusable usecases.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of agent. Acts as an identifier."
            },
            "description": {
                "type": "string",
                "description": "A description of the agent - features, roles, functionalities of the agent etc."
            },
            "custom_instructions": {
                "type": "string",
                "description": "Agent instructions which go into system message, appended to the default agent instructions as custom instructions."
            },
            "functions_to_add": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Function(s) names to add to agent. Functions must already exist."
            },
            "functions_to_remove": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Function(s) names to remove from agent."
            },
            "category": {
                "type": "string",
                "description": "A category to sort agent based on predefined categories. Only used when creating agent.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming", "planning", "user"]
            },
            "capability": {
                "type": "number",
                "description": "The capability of the agent, represented as an integer. This is calculated as a bitwise OR of capability masks. Each bit represents a different capability: 1 for INFO, 2 for CODE_INTERPRETER_TOOL, 4 for RETRIEVAL_TOOL, 8 for FILES, and 16 for MANAGEMENT. Bit 1 (INFO) must always be enabled. Combine capabilities by adding the values of their masks together."
            }
        },
        "required": ["name"]
    },
}

upsert_group_spec = {
    "name": "upsert_group",
    "category": "communication",
    "class_name": "GroupService.upsert_group",
    "description": "Upsert a group.",
    "parameters": {
        "type": "object",
        "properties": {
            "group": {"type": "string", "description": "The name of group. Acts as an indentifier."},
            "description": {"type": "string", "description": "Concise description of group. Is used when discovering groups so make sure it covers feautures, functions and roles within the group. You can also update it as you add/remove agents. A group should have atleast 1 MANAGER to be able to terminate it. Don't add agents for the sake of making a functional group, each agent must serve a valid purpose to the task at hand."},
            "agents_to_add": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Agent(s) to invite to group. Agents being added must be important to solve the groups task."
            },
            "agents_to_remove": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Agent(s) to remove from group."
            },
        },
        "required": ["group", "description"],
    },
}

discover_functions_spec = {
    "name": "discover_functions",
    "category": "programming",
    "class_name": "FunctionsService.discover_functions",
    "description": "Discover general purpose functions available using natural query.",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "A category to filter agents based on predefined categories.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "planning", "programming"]
            },
            "query": {
                "type": "string",
                "description": "A natural language query describing the desired features/functionalities. This can be left empty if not sure. If empty it will look for up to the first 10 functions in the category specified."
            }
        },
        "required": ["category"]
    },
}
upsert_function_spec = {
    "name": "upsert_function",
    "category": "programming",
    "class_name": "FunctionsService.upsert_function",
    "description": (
        "Endpoint for defining or updating modular functions for diverse applications. "
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
                    "Parameters are injected as global variables. Pydantic model: OpenAIParameter."
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


upload_file_spec = {
    "name": "upload_file",
    "category": "communication",
    "class_name": "AgentService.upload_file",
    "description": "Upload a file to OpenAI to be used by online assistant tools like code interpreter and retrieval.",
    "parameters": {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "A short description of the file.",
            },
            "data_or_url": {
                "type": "string",
                "description": "File data text, or a URL for where the file is which will be downloaded before uploading to OpenAI.",
            },
        },
        "required": ["description", "data_or_url"],
    },
}

delete_files_spec = {
    "name": "delete_files",
    "category": "programming",
    "class_name": "AgentService.delete_files",
    "description": "Delete OpenAI file(s) linked to an agent.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "File(s) to delete from agent."
            },
        },
        "required": ["file_ids"],
    },
}

get_file_content_spec = {
    "name": "get_file_content",
    "category": "programming",
    "class_name": "AgentService.get_file_content",
    "description": "Get contents of an OpenAI file.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_id": {
                "type": "string",
                "description": "File reference to get contents of.",
            },
        },
        "required": ["file_id"],
    },
}

serper_spec = {
    "name": "web_search",
    "category": "communication",
    "class_name": "SerperWrapper.run",
    "description": "Generic web search, access the internet through a search engine.",
    "status": "accepted",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query",
            },
            "max_results": {
                "type": "string",
                "description": "Maximum search results to include, defaults to 8.",
            },
        },
        "required": ["query"],
    },
}
group_info_function_specs = [
    get_group_info_spec,
    get_function_info_spec,
    get_agent_info_spec,
    upsert_function_spec
]

management_function_specs = [
    send_message_spec,
    discover_agents_spec,
    upsert_agent,
    discover_groups_spec,
    upsert_group_spec,
    discover_functions_spec,
    terminate_group_spec
]

files_function_specs = [
    upload_file_spec,
    delete_files_spec,
    get_file_content_spec
]

external_function_specs = [
    serper_spec,
]
