send_message_spec = {
    "name": "send_message_to_group",
    "category": "communication",
    "class_name": "GroupService.send_message_to_group",
    "description": "Sends a message to another group, terminating the sender's group and awaiting a response to continue.",
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
    "description": "Terminates a group, returning control with a response if tasked by another group.",
    "parameters": {
        "type": "object",
        "properties": {
            "group": {
                "type": "string",
                "description": "Group to terminate."
            },
            "response": {
                "type": "string",
                "description": "Summary of discussion and response to dependent group."
            }
        },
        "required": ["group", "response"]
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
    "description": "Retrieves information about a group including communication stats and members.",
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
    "description": "Provides information about a specific function.",
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
    "description": "Fetches details about a specific agent.",
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
    "description": "Creates or updates an agent for reusable use cases.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Identifier for the agent."
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
                "description": "The capability of the agent, represented as an integer. This is calculated as a bitwise OR of capability masks. Each bit represents a different capability: 1 for INFO, 2 for CODE_INTERPRETER, 4 for RETRIEVAL, 8 for FILES, and 16 for MANAGEMENT. Bit 1 (INFO) must always be enabled. Combine capabilities by adding the values of their masks together."
            }
        },
        "required": ["name"]
    }
}

upsert_group_spec = {
    "name": "upsert_group",
    "category": "communication",
    "class_name": "GroupService.upsert_group",
    "description": "Creates or updates a group. Each group must have atleast 3 agents. Each group must have atleast 1 agent with MANAGEMENT capabilities.",
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
            }
        },
        "required": ["group", "description"]
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
    "description": "Uploads a file for use by OpenAI tools.",
    "parameters": {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "Description of the file."
            },
            "data_or_url": {
                "type": "string",
                "description": "File data or URL for download."
            }
        },
        "required": ["description", "data_or_url"]
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
            "file_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "IDs of files to delete."
            }
        },
        "required": ["file_ids"]
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
    "category": "communication",
    "class_name": "WebSearchSerperWrapper.run",
    "description": "Performs a generic search for real-time web access through a search engine query.",
    "status": "accepted",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query."
            },
            "max_results": {
                "type": "string",
                "description": "Max number of search results."
            }
        },
        "required": ["query"]
    }
}

group_info_function_specs = [
    get_group_info_spec,
    get_function_info_spec,
    get_agent_info_spec,
    upsert_function_spec,
    discover_agents_spec,
    discover_groups_spec,
    discover_functions_spec,
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
]
