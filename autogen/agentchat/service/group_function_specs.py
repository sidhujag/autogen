send_message_spec = {
    "name": "send_message",
    "category": "communication",
    "class_name": "AgentService.send_message",
    "description": "Send a message from calling agent to another agent or all agents in a group via sending to group chat.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "The content of the message."},
            "recipient": {"type": "string", "description": "The name of the recipient agent or a group manager of any group you are in."},
            "request_reply": {"type": "boolean", "description": "Flag to request a reply from the recipient. Defaults to False."}
        },
        "required": ["message", "recipient"]
    }
}

create_or_update_group_spec = {
    "name": "create_or_update_group",
    "category": "communication",
    "class_name": "GroupService.create_or_update_group",
    "description": "Create or update a group. Groups are discoverable via the 'groups' category..",
    "parameters": {
        "type": "object",
        "properties": {
            "group": {"type": "string", "description": "The name of group. Acts as an indentifier."},
            "description": {"type": "string", "description": "Short description of group."},
            "system_message": {"type": "string", "description": "A system message for group, if any."},
            "agents_to_add": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Agent(s) to invite to group. Group agents can only see the context of the conversation of that group from the moment they join."
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


discover_agents_spec = {
    "name": "discover_agents",
    "category": "communication",
    "class_name": "AgentService.discover_agents",
    "description": "Allows agents to discover other agents based on specific queries. Agents can be searched via a natural query of required features or based on the specified categories. Agent names and descriptions are returned.",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "A category to filter agents based on predefined categories. To find group managers (group admins) use groups category (if not in group then subsequently can try to join these groups by getting an invite from someone in the group including group manager). 'user' group is for different agents to proxy user communication",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming", "planning", "groups", "user"]
            },
            "query": {
                "type": "string",
                "description": "A natural language query describing the desired features, functions, or functionalities of the agent being searched for."
            }
        },
        "required": ["query"]
    },
}

create_or_update_agent = {
    "name": "create_or_update_agent",
    "category": "communication",
    "class_name": "AgentService.create_or_update_agent",
    "description": "Create or update an agent. If you are creating an agent for purpose of adding functions to run code, consider for simple tasks just to create code and agents will execute it. Creating an agent means it will be reusable in other contexts widely. You can not update other agents, caller is authenticated.",
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
                "description": "Function(s) to add to agent. Functions must already exist."
            },
            "functions_to_remove": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Function(s) to remove from agent."
            },
            "category": {
                "type": "string",
                "description": "A category to sort agent based on predefined categories. Set this if creating a new agent. 'groups' not available here if that is what you are looking for, to make new group use create_or_update_group function.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming", "planning", "user"]
            }
        },
        "required": ["name"]
    },
}

discover_functions = {
    "name": "discover_functions",
    "category": "programming",
    "class_name": "FunctionsService.discover_functions",
    "description": "Allows agents to discover other agents based on specific queries. Agents can be searched via a natural query of required features or based on the specified categories. function names and descriptions are returned.",
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
                "description": "A natural language query describing the desired features/functionalities of the agent being searched for. This can be left empty if not sure. If empty it will look for up to the first 10 functions in the category specified."
            }
        },
        "required": ["category"]
    },
}

define_function = {
    "name": "define_function",
    "category": "programming",
    "class_name": "FunctionsService.define_function",
    "description": "Define a new function through code to add to the environment after you have tested the code to be working. Useful for non-niche generic code that may benefit from reuse. Necessary Python packages must be imported. External packages must be installed in the code through subprocess (avoids ModuleNotFoundError). Only add code that has been tested. After creating, test the function and fix any issues.",
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
            "code": {
                "type": "string",
                "description": "Python code to be executed. Make sure to include any imports that are needed. Make sure your code is standalone. Follow proper Python syntax. Assume parameters available as global variables."
            },
            "category": {
                "type": "string",
                "description": "A category to filter functions based on predefined categories.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "planning", "programming"]
            },
        },
        "required": ["name", "description", "code", "category"],
    },
}

group_function_specs = [
    send_message_spec,
    create_or_update_group_spec,
    discover_agents_spec,
    create_or_update_agent,
    discover_functions,
    define_function, 
]
