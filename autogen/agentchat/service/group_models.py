from autogen.agentchat.service import UpsertGroupModel, AuthAgent
import json
web_search_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="web_search_group",
    description="The web_search_group specializes in conducting comprehensive web searches, delivering well-structured and detailed information on diverse topics. It consists of the web_search_planner, web_search_worker, web_search_checker, and web_search_manager. The planner formulates effective search queries, the agent executes these queries and gathers information, and the QA ensures accuracy and relevance. The manager oversees operations, ensuring smooth collaboration and that the final output is self-contained, clear, and ready for presentation to the calling group. The group operates under three search moods: 'Strict' for precise and specific queries, 'Relaxed' for broader searches, and 'Abstract' for conceptual and thematic searches. Only web_search_checker can terminate the group.",
    agents_to_add=["web_search_planner", "web_search_worker", "web_search_checker", "web_search_manager"],
    locked = True
)

planning_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="planning_group",
    description="The Planning Group tackles problems by creating detailed, step-by-step plans for their resolution. plan_worker will create the plan, plan_checker will check the plan and plan_manager will coordinate the group and ensure worker and checker work effectively to create an optimal detailed plan. Only plan_manager can terminate the group.",
    agents_to_add=["plan_worker", "plan_checker", "plan_manager"],
    locked = True
)

openai_coding_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="openai_coding_group",
    description="The OpenAI Coding Group develops code solutions based on provided step-by-step plans. In the absence of a plan, the group is proactive in requesting one unless its a simple request. openai_code_worker will write the code, openai_code_checker will run and be quality assurance as well as write tests and openai_code_manager will coordinate the group and ensure worker and checker work effectively to create optimal working code. Only openai_code_manager can terminate the group. Create a function if code created is meant to be reusable through the 'function_creation_group'.",
    agents_to_add=["openai_code_worker", "openai_code_checker", "openai_code_manager"],
    locked = True
)

local_coding_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="local_coding_group",
    description="The Local Coding Group mirrors the structure of the OpenAI Coding Group but focuses on local development environments and emphasizes the creation of reusable functions through the 'function_creation_group'.",
    agents_to_add=["local_code_worker", "local_code_checker", "local_code_manager"],
    locked = True
)

functions_coding_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="function_creation_group",
    description="The Function Creation Group mirrors the structure of the Local and OpenAI Coding group but specializes in developing, testing, and refining reusable functions, ensuring they meet high standards of quality and efficiency. function_code_worker will create the function, function_checker will sanity check the function fields and test the function execution. function_checker will also transition the function from development to testing and finally to acceptance once accepted. function_manager will oversee the creation and testing process to ensure it goes smoothly.",
    agents_to_add=["function_code_worker", "function_checker", "function_manager"],
    locked = True
)

json_zapier_spec = {"openapi":"3.0.2","info":{"title":"Zapier AI Actions for Agents (Dynamic)","version":"1.0.0","description":"Equip Agents with the ability to run thousands of actions via Zapier through natural language interactions."},"servers":[{"url":"https://actions.zapier.com"}],"paths":{"/gpt/api/v1/available/":{"get":{"operationId":"list_available_actions","summary":"List Available Actions","parameters":[{"in":"query","name":"apps","schema":{"title":"Apps","description":"Filter actions to a comma separated list of Zapier app names.","type":"string"},"required":False,"description":"Filter actions to a comma separated list of Zapier app names."},{"in":"query","name":"exact_search","schema":{"title":"Exact Search","description":"Filter actions to exact search string of the description (case insensitive).","type":"string"},"required":False,"description":"Filter actions to exact search string of the description (case insensitive)."}],"responses":{"200":{"description":"OK","content":{"application/json":{"schema":{"$ref":"#/components/schemas/AvailableActionResponseSchema"}}}}},"description":"List all the currently available actions for the user. If you try to run an action and receive an error\n that it does not exist, try refreshing this list first.","security":[{"ApiKeyAuth":[]}]}},"/gpt/api/v1/available/{available_action_id}/run/":{"post":{"operationId":"run_action","summary":"Run Action","parameters":[{"in":"path","name":"available_action_id","schema":{"title":"Available Action Id","type":"string","pattern":"^[A-Z0-9]{26}$","example":"01ARZ3NDEKTSV4RRFFQ69G5FAV"},"required":True,"example":"01ARZ3NDEKTSV4RRFFQ69G5FAV"}],"responses":{"200":{"description":"OK","content":{"application/json":{"schema":{"$ref":"#/components/schemas/RunResponse"}}}},"400":{"description":"Bad Request","content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}}}},"description":"Run an available action using plain english instructions. You may also include associated params from list_available_actions in the body of the request.","requestBody":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/RunRequest"}}},"required":True},"security":[{"ApiKeyAuth":[]}]}}},"components":{"schemas":{"AvailableActionSchema":{"title":"AvailableActionSchema","type":"object","properties":{"id":{"title":"Id","description":"The unique ID of the available action.","type":"string"},"operation_id":{"title":"Operation Id","description":"The operation ID of the available action.","type":"string"},"description":{"title":"Description","description":"Description of the action.","type":"string"},"params":{"title":"Params","description":"Available hint fields for the action.","type":"object"}},"required":["id","operation_id","description","params"]},"AvailableActionResponseSchema":{"title":"AvailableActionResponseSchema","type":"object","properties":{"results":{"title":"Results","type":"array","items":{"$ref":"#/components/schemas/AvailableActionSchema"}},"configuration_link":{"title":"Configuration Link","description":"Guide the user to setup new natural language actions with the configuration_link. You can optionally add ?setup_action=... onto configuration_link to set up a specific Zapier app and action For example: https://actions.zapier.com/gpt/start?setup_action=gmail find email","type":"string"}},"required":["results","configuration_link"]},"RunResponse":{"title":"RunResponse","description":"This is a summary of the results given the action that was run.","type":"object","properties":{"id":{"title":"Id","description":"The id of the run log.","type":"string"},"action_used":{"title":"Action Used","description":"The name of the action that was run.","type":"string"},"input_params":{"title":"Input Params","description":"The params we used / will use to run the action.","type":"object"},"review_url":{"title":"Review Url","description":"The URL to run the action or review the AI choices the AI made for input_params given instructions.","type":"string"},"result":{"title":"Result","description":"A trimmed down result of the first item of the full results. Ideal for humans and language models!","type":"object"},"additional_results":{"title":"Additional Results","description":"The rest of the full results. Always returns an array of objects","type":"array","items":{"type":"object"}},"result_field_labels":{"title":"Result Field Labels","description":"Human readable labels for some of the keys in the result.","type":"object"},"status":{"title":"Status","description":"The status of the action run.","default":"success","enum":["success","error","empty","preview"],"type":"string"},"error":{"title":"Error","description":"The error message if the action run failed.","type":"string"},"assistant_hint":{"title":"Assistant Hint","description":"A hint for the assistant on what to do next.","type":"string"},"full_results":{"title":"Full Results","description":"The full results, not summarized, if available. Always returns an array of objects.","type":"array","items":{"type":"object"}}},"required":["id","action_used","input_params","review_url","additional_results","full_results"]},"ErrorResponse":{"title":"ErrorResponse","type":"object","properties":{"error":{"title":"Error","description":"Error message.","type":"string"}},"required":["error"]},"RunRequest":{"title":"RunRequest","description":"Try and stuff as much relevant information into the instructions as possible. Set any necessary AvailableActionSchema params. This type of action allows optionally setting preview_only if the user wants to preview before running.","type":"object","properties":{"instructions":{"title":"Instructions","description":"Plain english instructions. Provide as much detail as possible, even if other fields are present.","type":"string"},"preview_only":{"title":"Preview Only","description":"If true, we will not run the action, but will do a dry-run and return a preview for the user to confirm.","default":False,"type":"boolean"}},"required":["instructions"]}},"securitySchemes":{"ApiKeyAuth":{"type":"apiKey","in":"header","name":"X-API-KEY"}}}}
spec_string = json.dumps(json_zapier_spec)
zapier_group_model = UpsertGroupModel(
    auth=AuthAgent(api_key='', namespace_id=''),
    name="zapier_integration_group",
    description=(
       "The Zapier Integration Group is dedicated to harnessing the power of APIs with almost infinite capabilities for seamless workflow automation and integration via Zapier. Our team specializes in connecting a wide array of applications, facilitating data transfer, and automating tasks across platforms (google suite, ). We focus on setting up and managing Zaps, ensuring robust API interactions, and optimizing processes for efficiency and reliability. Key activities include API configuration, testing Zapier integrations, and customizing automation to align with specific workflow requirements.\n\n"
        "### RULES"
        "**Step 1:** Based on the user's query, call `/list_available_actions/` from the SCHEMA provided below. This step checks for the availability of the required Zapier AI Actions."
        "**Step 2:** If the required action(s) are available, proceed directly to Step 4. If not, provide the user with the configuration link for the required action(s). Instruct them to inform you once they have enabled the Zapier AI Action. Use the format `https://actions.zapier.com/gpt/start?setup_action=[ACTION_NAME]&setup_params=[PARAMS]` for the configuration link, where `[ACTION_NAME]` is the name or description of the action in natural language and `[PARAMS]` are any specific instructions or settings you want to apply."
        "**Step 3:** Once the user confirms they have configured the required action, continue with their original request."
        "**Step 4:** If the action is available, use the `available_action_id` (returned as the `id` field within the `results` array in the JSON response from `/list_available_actions`). Fill in the necessary details for the `run_action` operation. Base your instructions and any additional fields on the request. If your action requires AI to make guesses or decisions, specify this in the `setup_params` when providing the configuration link in Step 2."
        "For example, if you need to set up an action for Google Calendar to find an event and want the AI to guess the start and end times, you would use the following URL in Step 2: `https://actions.zapier.com/gpt/start?setup_action=google calendar find event&setup_params=set have AI guess for Start and End time`."
        "### SCHEMA:\n" + spec_string
    ),
    agents_to_add=["api_tester", "api_caller"],
    locked=True
)

external_group_models = [
    web_search_group_model,
    planning_group_model,
    openai_coding_group_model,
    local_coding_group_model,
    functions_coding_group_model,
    zapier_group_model
]
