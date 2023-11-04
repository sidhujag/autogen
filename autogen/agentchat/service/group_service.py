
from .. import ConversableAgent
from typing import List

class GroupService:
    @staticmethod
    def create_or_update_group(sender: ConversableAgent, group: str, description: str, agents_to_add: List[str] = None, agents_to_remove: List[str] = None, system_message: str = None) -> str:
        from . import MakeService, UpsertAgentModel
        agents, err = MakeService.upsert_agents([UpsertAgentModel(
            auth=sender.auth,
            name=group,
            description=description,
            system_message=system_message,
            agents_to_add=agents_to_add,
            agents_to_remove=agents_to_remove,
            group=True,
            category="groups"
        )])
        if err is not None:
            return f"Could not update group: {err}", None
        return "Group updated!", agents[0]

