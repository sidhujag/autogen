send_message_spec = {
    "name": "send_message_to_group",
    "category": "communication",
    "class_name": "GroupService.send_message_to_group",
    "description": "Send a message to another group to delegate a task. When you send a message to another group your current group will terminate and upon termination of the recipient group a response will be sent back to you so your group can continue.",
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
            "response": {"type": "string", "description": "Summary of group discussion and response back to the group delegating to you or if no delegation then the user."},
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
    "description": "Upsert a function with code. Test any code before adding and run the function to test it after creating, fix it if broken. You may have to add function to an agent and agent to group to run it.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the function to define.",
            },
            "description": {
                "type": "string",
                "description": "A short description of the function.",
            },
            "parameters": {
                "type": "string",
                "description": "JSON schema of the parameters object encoded as a string. Use the standard OpenAPI 2.0 specification for parameters in function calling, and examples of functions already attached to see format. These are injected as global variables.",
            },
            "function_code": {
                "type": "string",
                "description": "Python code. Make sure to include any imports that are needed. Make sure your code is standalone. Follow proper Python syntax. Assume 'parameters' available as global variables. Use stdout for output to log so execution can get results. To solve ModuleNotFoundError you can import external packages by code like: 'import subprocess\nsubprocess.run([\"pip\", \"-qq\", \"install\", [package1,package2]])' where package1..x are your external package names."
            },
            "category": {
                "type": "string",
                "description": "A category to filter functions based on predefined categories. Set when creating a new function.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "planning", "programming"]
            },
        },
        "required": ["name", "function_code"],
    },
}


upload_file_spec = {
    "name": "upload_file",
    "category": "programming",
    "class_name": "AgentService.upload_file",
    "description": "Upload a file to be used by assistant tools like code interpreter and retrieval.",
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
    "description": "Delete file(s) linked to an agent.",
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
    "description": "Get contents of a file.",
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
]

management_function_specs = [
    send_message_spec,
    discover_agents_spec,
    upsert_agent,
    discover_groups_spec,
    upsert_group_spec,
    discover_functions_spec,
    upsert_function_spec, 
    terminate_group_spec
]

files_function_specs = [
    upload_file_spec,
    delete_files_spec,
    get_file_content_spec
]
