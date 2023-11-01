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
            "group_chat": {"type": "string", "description": "The name of the group chat."},
            "hello_message": {"type": "string", "description": "A welcome message, if any. Maybe describe your skills and invite others to send you a message so you can solve a task for the group."}
        },
        "required": ["group_chat"],
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
            "group_chat": {"type": "string", "description": "The name of the group chat."},
            "invite_message": {"type": "string", "description": "An invitation message, if any. The receiving agent does not have to join but usually will as he is invited for his specific skills."}
        },
        "required": ["agent_name", "group_chat"],
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
            "group_chat": {"type": "string", "description": "The name of the new group."},
            "group_description": {"type": "string", "description": "Short description of the new group."},
            "system_message": {"type": "string", "description": "A system message for the new group, if any."},
            "invitees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Array of agents to invite to new group."
            },
        },
        "required": ["group_chat", "group_description"],
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
            "group_chat": {"type": "string", "description": "The name of the group chat."},
            "goodbye_message": {"type": "string", "description": "A farewell message, if any."}
        },
        "required": ["group_chat"],
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
    "description": "Create or update an agent. If you are creating an agent for purpose of adding functions to run code, consider for simple tasks just to create code and agents will execute it. Creating an agent means it will be reusable in other contexts widely.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent_name": {
                "type": "string",
                "description": "The name of agent to create or update, must be unique to all agents."
            },
            "agent_description": {
                "type": "string",
                "description": "A description of the agent - features, roles, functionalities of the agent etc."
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
    "description": "Allows agents to discover other agents based on specific queries related to features, functions, functionalities, or categories. Agents can be searched via a natural query of required features or based on the specified categories. Function names and descriptions are returned. Usually paired with add_functions in a subsequent call.",
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
    "description": "Allows agents to add specific function ability to themselves. Usually paired with discover_functions.",
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
    "description": "Define a new function through code to add to the context of the agent. Double check the code will run successfully against the execution template script. Useful for generic functions that you think will be widely in many other contexts. Necessary Python packages must be declared. Will automatically add the function to agent.",
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
                "description": "The implementation in Python. The code is executed as part of a larger script that handles package installations, function definition, and function execution with the provided arguments. When defining a function, such as 'def your_function(a, b): ...', it will be executed as 'result = your_function(**args)'. The 'result' variable stores the output of your function. Ensure your code is standalone, follows Python syntax, and is thoroughly tested before defining a function. Here is a template of the execution script: 'import subprocess;\nsubprocess.run(['pip', 'install', ...]);\ndef your_function(...): ...;\nargs = {...};\nresult = your_function(**args);\nif result is not None:\n    print(result)'"
            },
            "category": {
                "type": "string",
                "description": "A category to filter functions based on predefined categories.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming"]
            },
        },
        "required": ["name", "description", "code", "category"],
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
    define_function,
    add_functions
]
