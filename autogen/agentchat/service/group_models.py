from autogen.agentchat.service import UpsertGroupModel, AuthAgent   
web_search_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_group",
    description="The web_search_group specializes in conducting comprehensive web searches, delivering well-structured and detailed information on diverse topics. It consists of the web_search_planner, web_search_agent, web_search_qa, and web_search_manager. The planner formulates effective search queries, the agent executes these queries and gathers information, and the QA ensures accuracy and relevance. The manager oversees operations, ensuring smooth collaboration and that the final output is self-contained, clear, and ready for presentation to the calling group. This group operates under three search moods: Strict, Relaxed, and Abstract, to tailor the search specificity to the request. Only web_search_qa can terminate the group. The group's agents have been configured with the correct capabilities to do their job.",
    agents_to_add=["web_search_planner", "web_search_agent", "web_search_qa", "web_search_manager"],
    locked = True
)

planning_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="planning_group",
    description="Planning group, you will get a problem where you need to create a detailed step-by-step plan on how to solve the problem. plan_worker will create the plan, plan_checker will check the plan and plan_manager will coordinate the group and ensure worker and checker work effectively to create an optimal detailed plan. Only plan_manager can terminate the group. The group's agents have been configured with the correct capabilities to do their job.",
    agents_to_add=["plan_worker", "plan_checker", "plan_manager"],
    locked = True
)

external_group_models = [
    web_search_group_model,
    planning_group_model
]
