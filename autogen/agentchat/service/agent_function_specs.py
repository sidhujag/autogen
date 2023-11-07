send_message_spec = {
    "name": "send_message",
    "category": "communication",
    "class_name": "AgentService.send_message",
    "description": "Send a message to another agent.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "The content of the message. In the message you should if and when you expect a reply under what terms, conditions so that you can resolve your dependency."},
            "recipient": {"type": "string", "description": "The name of the recipient agent."}
        },
        "required": ["message", "recipient"]
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
                "description": "Function(s) names to add to agent. Functions must already exist. Functions are looked up when agents are recreated from database upon resynchronization."
            },
            "functions_to_remove": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Function(s) names to remove from agent."
            },
            "category": {
                "type": "string",
                "description": "A category to sort agent based on predefined categories. Set this if creating a new agent.",
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
    "description": "Allows agents to discover other agents based on specific queries.",
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
    "description": "Create or update a function with code. Upon creation only use code that has been validated/tested additionally modifying and validating changes as needed related to using the 'parameters' field for general purpose applicability. ",
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
                "description": "Python code to be executed. Make sure to include any imports that are needed. Make sure your code is standalone. Follow proper Python syntax. Assume parameters available as global variables."
            },
            "category": {
                "type": "string",
                "description": "A category to filter functions based on predefined categories.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "planning", "programming"]
            },
        },
        "required": ["name", "description", "function_code", "category"],
    },
}

agent_function_specs = [
    send_message_spec,
    discover_agents_spec,
    create_or_update_agent,
    discover_functions,
    define_function, 
]
