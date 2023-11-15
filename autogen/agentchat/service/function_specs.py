send_message_spec = {
    "name": "send_message_to_group",
    "category": "communication",
    "class_name": "GroupService.send_message_to_group",
    "description": "Send a message to another group to assign a task. When you send a message to another group your current group will terminate and upon termination of the recipient group a response will be sent back to you so your group can continue.",
    "parameters": {
        "type": "object",
        "properties": {
            "from_group": {"type": "string", "description": "The name of the sending group you are sending message from. A reference will be stored so a group can respond back to this group upon termination."},
            "to_group": {"type": "string", "description": "The name of the recipient group. It must be a valid existing group and have 3 or more agents inside it with atleast 1 being atleast as capable as a MANAGER."},
            "message": {"type": "string", "description": "The content of the message. In the message you should include full context of what your task is for the recipient group."},
        },
        "required": ["from_group", "to_group", "message"]
    }
}

terminate_group_spec = {
    "name": "terminate_group",
    "category": "communication",
    "class_name": "GroupService.terminate_group",
    "description": "Terminate and conclude a group. The groupchat has loop that continues to select a next speaker until it is terminated. This will let give control back to the caller with a summary. If another group sent you a task, from_group was saved as a reference which will be sent the response.",
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
    "description": "Get group info: Communication stats of the group as well as agents/files in group.",
    "parameters": {
        "type": "object",
        "properties": {
            "group": {
                "type": "string",
                "description": "The group name."
            }
        },
        "required": ["group"]
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
    "description": "Upsert an agent. Create an agent only for reusable isolated usecases.",
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
                "description": "Function(s) names to add to agent. This gives the groups the agent is in the ability to see the function. Functions must already exist."
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
                "description": "The capability of the agent, represented as an integer. This is calculated as a bitwise OR of capability masks. Each bit represents a different capability: 1 for GROUP_INFO, 2 for CODE_INTERPRETER_TOOL, 4 for RETRIEVAL_TOOL, 8 for FILES, and 16 for MANAGEMENT. Bit 1 (GROUP_INFO) must always be enabled. Combine capabilities by adding the values of their masks together."
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
            "description": {"type": "string", "description": "Concise description of group. Is used when discovering groups so make sure it covers feautures, functions and roles within the group. You can also update it as you add/remove agents. When calling function in a group the agent must be existing in the group otherwise you will get a function not found error. A group should have atleast 1 MANAGER to be able to terminate it. Don't add agents for the sake of making a functional group, each agent must serve a valid purpose to the task at hand."},
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
    "description": "This endpoint is for defining or updating a reusable function that encapsulate a set of operations. Functions should be black-box, handling input arguments dynamically to deliver expected outputs across various use cases. Avoid hardcoding values and ensure your function is adaptable. This function should include debug print statements during its development and testing phases to facilitate troubleshooting. Iterative refinement is expected, and the function should not be marked as 'accepted' until it meets all specified requirements and performs as intended.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The unique name for the function, serving as an identifier. Choose a name that reflects the function's general operation."
            },
            "description": {
                "type": "string",
                "description": "A concise summary of the function's purpose, behavior, and potential use cases. Highlight the general nature of the function."
            },
            "parameters": {
                "type": "string",
                "description": "Function arguments represented as a JSON object encoded as a string, in accordance with the OpenAPI 2.0 specification. These arguments should be designed to allow the function to operate in different scenarios and with various inputs. In addition to existing arguments, include a 'debug_mode' argument, which when set to `True`, activates detailed print statements throughout the function. Arguments are added automatically by the interpreter as global variables (key=value statements) accessible inside of function_code."
            },
            "function_code": {
                "type": "string",
                "description": "The executable Python code for the function. Ensure all required imports are included. The code should be modular and general-purpose, capable of handling a range of inputs specified through arguments. Outputs should be directed to stdout to facilitate result capture. It's recommended to include print statements or logging for debugging purposes, allowing you to verify and iterate on the function's behavior. If the function does not produce the expected results, use these debug outputs to identify and resolve issues before finalizing the function definition. Use 'debug_mode' argument to control debugging on stdout. Manage dependencies with subprocess calls to install external packages as needed."
            },
            "status": {
                "type": "string",
                "enum": ["development", "testing", "accepted"],
                "description": "Add a status attribute to the function's metadata to clearly indicate its development stage. Code should be iterated on until accepted for working code that others can use."
            },
            "category": {
                "type": "string",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "planning", "programming"],
                "description": "The category for the function, helping categorize and organize functions within the system for easier discovery and reuse."
            }
        },
        "required": ["name", "parameters", "function_code", "status"]
    }
}




upload_file_spec = {
    "name": "upload_file",
    "category": "programming",
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
group_info_function_specs = [
    get_group_info_spec,
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
