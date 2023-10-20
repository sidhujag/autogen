
send_message_spec = {
    "name": "send_message",
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
    "description": "Join a specified group if you have been already invited.",
    "parameters": {
        "type": "object",
        "properties": {
            "group_name": {"type": "string", "description": "The name of the group to join."},
            "hello_message": {"type": "string", "description": "A welcome message, if any. Maybe describe your skills and invite others to send you a message so you can solve a task for the group."}
        },
        "required": ["group_name"],
    },
}

invite_to_group_spec = {
    "name": "invite_to_group",
    "description": "Invite another agent to a specified group. Agents can only join if they have been invited.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent_name": {"type": "string", "description": "The name of the agent to invite."},
            "group_name": {"type": "string", "description": "The name of the group."},
            "invite_message": {"type": "string", "description": "An invitation message, if any. The receiving agent does not have to join but usually will as he is invited for his specific skills."}
        },
        "required": ["agent_name", "group_name"],
    },
}

create_group_spec = {
    "name": "create_group",
    "description": "Create a new group.",
    "parameters": {
        "type": "object",
        "properties": {
            "group_name": {"type": "string", "description": "The name of the new group."},
            "system_message": {"type": "string", "description": "A system message for the new group, if any."}
        },
        "required": ["group_name"],
    },
}

delete_group_spec = {
    "name": "delete_group",
    "description": "Delete an existing group.",
    "parameters": {
        "type": "object",
        "properties": {
            "group_name": {"type": "string", "description": "The name of the group to delete."}
        },
        "required": ["group_name"],
    },
}

leave_group_spec = {
    "name": "leave_group",
    "description": "Leave a specified group.",
    "parameters": {
        "type": "object",
        "properties": {
            "group_name": {"type": "string", "description": "The name of the group to leave."},
            "goodbye_message": {"type": "string", "description": "A farewell message, if any."}
        },
        "required": ["group_name"],
    },
}

discover_agents_spec = {
    "name": "discover_agents",
    "description": "Allows agents to discover other agents based on specific queries related to features, tools, functionalities, or categories. Agents can be searched via a natural query of required features or based on the specified categories.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A natural language query describing the desired features, tools, or functionalities of the agent being searched for. This can be left empty if not sure."
            },
            "category": {
                "type": "string",
                "description": "A category to filter agents based on predefined categories like 'information_retrieval', 'communication', 'data_processing', 'sensory_perception', and 'programming'.",
                "enum": ["information_retrieval", "communication", "data_processing", "sensory_perception", "programming"]
            }
        },
        "required": []
    }
}
# Aggregate all function specs into a list for easier import
group_function_specs = [
    send_message_spec,
    join_group_spec,
    invite_to_group_spec,
    create_group_spec,
    delete_group_spec,
    leave_group_spec,
    discover_agents_spec
]
