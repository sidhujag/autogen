from autogen.agentchat.service import UpsertGroupModel, AuthAgent   
web_search_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_group",
    description="The web_search_group is specialized in conducting comprehensive and accurate web searches, encompassing news, images, videos, and textual content. This group is a synergy of three key agents: the web_search_planner, web_search_agent, and web_search_qa. The web_search_planner is responsible for formulating effective search queries based on the initial request, ensuring a wide yet focused search scope. The web_search_agent executes these queries, gathering detailed and relevant information from various sources. Finally, the web_search_qa performs a critical quality assurance role, verifying the accuracy and completeness of the information collected. This group operates under three search moods: Strict, Relaxed, and Abstract, tailored to the specificity of the request. The group's collaborative effort ensures that the final information delivered is comprehensive, accurate, and well-structured, providing valuable insights back to the requester.",
    agents_to_add=["web_search_planner", "web_search_agent", "web_search_qa"]
)

external_group_models = [
    web_search_group_model,
]
