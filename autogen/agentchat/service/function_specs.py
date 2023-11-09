send_message_spec = {
    "name": "send_message_to_group",
    "category": "communication",
    "class_name": "GroupService.send_message_to_group",
    "description": "Send a message to another group to resolve a dependency.",
    "parameters": {
        "type": "object",
        "properties": {
            "from_group": {"type": "string", "description": "The name of the sending group you are sending message from. Useful for response purposes."},
            "to_group": {"type": "string", "description": "The name of the recipient group. It must be a valid existing group and have more than 2 agents inside it."},
            "message": {"type": "string", "description": "The content of the message. In the message you should include full context of what your dependency is and when and what format the response to the 'from_group' should be."},
        },
        "required": ["from_group", "to_group", "message"]
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
    "description": "Get group info: Which agents are in the group and stats in the group.",
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
            "description": {"type": "string", "description": "Concise description of group. Is used when discovering groups so make sure it covers feautures, functions and roles within the group. You can also update it as you add/remove agents. When calling function in a group the agent must be existing in the group otherwise you will get a function not found error."},
            "agents_to_add": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Agent(s) to invite to group."
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
    "description": "Upsert a function with code. Upon creation only use code that has been validated/tested additionally modifying and validating changes as needed related to using the 'parameters' field for general purpose applicability. Functions may be added to agents and called within groups if those agents are part of that group.",
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
                "description": "Python code to be executed. Make sure to include any imports that are needed. Make sure your code is standalone. Follow proper Python syntax. Assume parameters available as global variables. Use stdout for output to log so execution can get results. To solve ModuleNotFoundError you can import external packages by code like: 'import subprocess\nsubprocess.run([\"pip\", \"-qq\", \"install\", [package1,package2]])' where package1..x are your external package names."
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

function_specs = [
    get_group_info_spec,
    send_message_spec,
    discover_agents_spec,
    upsert_agent,
    discover_groups_spec,
    upsert_group_spec,
    discover_functions_spec,
    upsert_function_spec, 
]
