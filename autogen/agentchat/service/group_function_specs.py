send_message_spec = {
    "name": "send_message",
    "category": "communication",
    "class_name": "AgentService.send_message",
    "description": "Send a message to an individual agent or to all agents in a group via the group manager.",
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

join_group_spec = {
    "name": "join_group",
    "category": "communication",
    "class_name": "GroupService.join_group",
    "description": "Join a specified group if you have been already invited. Groups are referenced by the group manager name.",
    "parameters": {
        "type": "object",
        "properties": {
            "group_agent_name": {"type": "string", "description": "The name of the group agent who manages the group."},
            "hello_message": {"type": "string", "description": "A welcome message, if any. Maybe describe your skills and invite others to send you a message so you can solve a task for the group."}
        },
        "required": ["group_agent_name"],
    },
}

invite_to_group_spec = {
    "name": "invite_to_group",
    "category": "communication",
    "class_name": "GroupService.invite_to_group",
    "description": "Invite another agent to a specified group. Agents can only join if they have been invited.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "The name of the agent to invite."},
            "group_agent_name": {"type": "string", "description": "The name of the group agent who manages the group."},
            "invite_message": {"type": "string", "description": "An invitation message, if any. The receiving agent does not have to join but usually will as he is invited for his specific skills."}
        },
        "required": ["agent_name", "group_agent_name"],
    },
}

create_group_spec = {
    "name": "create_group",
    "category": "communication",
    "class_name": "GroupService.create_group",
    "description": "Create a new group. Group manager agent is automatically placed in the 'groups' category. The calling agent will be automatically added to the group upon creation.",
    "parameters": {
        "type": "object",
        "properties": {
            "group_agent_name": {"type": "string", "description": "The name of the new group agent who will manage the group."},
            "group_description": {"type": "string", "description": "Short description of the new group."},
            "system_message": {"type": "string", "description": "A system message for the new group, if any."},
            "invitees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Array of agents to invite to new group."
            },
        },
        "required": ["group_agent_name", "group_description"],
    },
}

leave_group_spec = {
    "name": "leave_group",
    "category": "communication",
    "class_name": "GroupService.leave_group",
    "description": "Leave a specified group.",
    "parameters": {
        "type": "object",
        "properties": {
            "group_agent_name": {"type": "string", "description": "The name of the group agent who manages the group. If you are the last agent to leave, the group gets deleted automatically."},
            "goodbye_message": {"type": "string", "description": "A farewell message, if any."}
        },
        "required": ["group_agent_name"],
    },
}

discover_agents_spec = {
    "name": "discover_agents",
    "category": "communication",
    "class_name": "AgentService.discover_agents",
    "description": "Allows agents to discover other agents based on specific queries related to features, functions, functionalities, or categories. Agents can be searched via a natural query of required features or based on the specified categories. Agent names and descriptions are returned.",
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
                "description": "A natural language query describing the desired features, functions, or functionalities of the agent being searched for. This can be left empty if not sure. If empty it will return the first 10 agents in the specified category."
            }
        },
        "required": ["category"]
    },
}

create_or_update_agent = {
    "name": "create_or_update_agent",
    "category": "communication",
    "class_name": "AgentService.create_or_update_agent",
    "description": "Create or update an agent.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent_name": {
                "type": "string",
                "description": "The name of agent to create or update, must be unique to all agents."
            },
            "description": {
                "type": "string",
                "description": "A description of the features, functions, or functionalities of the agent."
            },
            "function_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Array of function names. Will upsert the functions to agent database."
            },
            "category": {
                "type": "string",
                "description": "A category to sort agent based on predefined categories. Set this if creating a new agent. 'groups' not available here if that is what you are looking for, to make new group use create_group function.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming", "planning", "user"]
            }
        },
        "required": ["agent_name"]
    },
}

discover_functions = {
    "name": "discover_functions",
    "category": "programming",
    "class_name": "FunctionsService.discover_functions",
    "description": "Allows agents to discover other agents based on specific queries related to features, functions, functionalities, or categories. Agents can be searched via a natural query of required features or based on the specified categories. An agent can add the returned function(s) via add_functions so they can subsequently be called. Function names and descriptions are returned.",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "A category to filter agents based on predefined categories.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming"]
            },
            "query": {
                "type": "string",
                "description": "A natural language query describing the desired features, functions, or functionalities of the agent being searched for. This can be left empty if not sure. If empty it will look for up to the first 10 functions in the category specified."
            }
        },
        "required": ["category"]
    },
}

add_functions = {
    "name": "add_functions",
    "category": "programming",
    "class_name": "FunctionsService.add_functions",
    "description": "Allows agents to add specific function ability to themselves, usually you would discover functions prior to adding. Once added, the agent may decide to use this function.",
    "parameters": {
        "type": "object",
        "properties": {
            "function_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Array of function names. Will upsert functions to agent database."
            },
        },
        "required": ["function_names"]
    },
}

define_function = {
    "name": "define_function",
    "category": "programming",
    "class_name": "FunctionsService.define_function",
    "description": "Define a new function through python code to add to the context of the agent. Necessary Python packages must be declared. Once defined, the agent may decide to use this function, respond with a normal message. Will upsert the functions to agent database.",
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
                "description": "JSON schema of the parameters object encoded as a string. Use the standard OpenAPI 2.0 specification, and examples of functions already attached to see format.",
            },
            "packages": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Array of package names imported by the function encoded as an array. Packages need to be installed with pip prior to invoking the function. This solves ModuleNotFoundError. Should also include code."
            },
            "code": {
                "type": "string",
                "description": "The implementation in Python. Do not include the function declaration. You should include either one of code or class_name but not both.",
            },
            "class_name": {
                "type": "string",
                "description": "If code is not provided but a class_name object to invoke when function is called. Follows pattern of [class].[name] where class is the class of the python class and name is the function name. Example: FunctionsService.add_functions. You should include either one of code or class_name but not both.",
            },
            "category": {
                "type": "string",
                "description": "A category to filter functions based on predefined categories.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming"]
            },
        },
        "required": ["name", "description", "category"],
    },
}

group_function_specs = [
    send_message_spec,
    join_group_spec,
    invite_to_group_spec,
    create_group_spec,
    leave_group_spec,
    discover_agents_spec,
    create_or_update_agent,
    discover_functions,
    define_function
]
