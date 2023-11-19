from autogen.agentchat.service import UpsertAgentModel, AuthAgent, MANAGEMENT, INFO, CODE_INTERPRETER, FILES, RETRIEVAL     
web_search_agent_model = UpsertAgentModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_agent",
    category="information_retrieval",
    description="Uses tools to find information through search engines and possibly summarizes results.",
    system_message="Uses web_search tool to perform real-time online searches and summarize the results based upon request. Summarize by default unless you are asked to give raw results. May use retrieval tool with files for large knowledge bases and results. Retrieval tool will take a file and automatically chunk it and give you RAG ability to query the file contents.",
    human_input_mode="NEVER",
    capability=INFO | FILES | RETRIEVAL,
    functions_to_add=["web_search"]
)

external_agent_models = [
    web_search_agent_model,
]
