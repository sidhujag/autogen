        
import json
import sys

from ..contrib.gpt_assistant_agent import GPTAssistantAgent
from typing import List, Any, Optional, Dict, Tuple
from pydantic import ValidationError
from autogen.code_utils import (
    execute_code
)

class FunctionsService:
    @staticmethod
    def discover_functions(sender: GPTAssistantAgent, category: str, query: str = None) -> str:
        from . import BackendService, DiscoverFunctionsModel
        response, err = BackendService.discover_backend_functions(DiscoverFunctionsModel(auth=sender.auth, query=query, category=category))
        if err is not None:
            return err
        return response
    
    @staticmethod
    def execute_func(function_code: str, **args):
        global_vars_code = '\n'.join(f'{key} = {repr(value)}' for key, value in args.items())
        str_code = f"{global_vars_code}\n\n{function_code}"
        exitcode, logs, env = execute_code(str_code)
        exitcode2str = "execution succeeded" if exitcode == 0 else "execution failed"
        if logs == "" and exitcode2str == "execution succeeded":
            exitcode2str = "no output found, make sure function uses stdout to output results"
        if logs == "" or exitcode != 0:
            return f"Broken function code! (PLEASE FIX using upsert_function with new function_code). exitcode: {exitcode} ({exitcode2str})\nCode output: '{logs}'\n\nfunction_code:\n```python {function_code}\n```"
        return f"exitcode: {exitcode} ({exitcode2str})\nCode output: '{logs}'.\nNote even though it ran successfully you may still need to update the code if results do not match as expected. Iterate to fix function_code (via upsert_function) until you are happy.\n\nfunction_code:\n```python {function_code}\n``"

    @staticmethod
    def _find_class(class_name):
        for module in sys.modules.values():
            cls = getattr(module, class_name, None)
            if cls is not None:
                return cls
        return None

    @staticmethod
    def define_function_internal(
        agent: GPTAssistantAgent,
        function
    ) -> str:
        from .backend_service import OpenAIParameter
        function.parameters = function.parameters or OpenAIParameter()
        
        # Prepare the function tool configuration
        function_tool_config = {
            "type": "function",
            "function": {
                "name": function.name,
                "description": function.description,
                "parameters": function.parameters.dict(exclude_none=True)
            }
        }
        
        # Check if a tool with the same name already exists
        if 'tools' not in agent.llm_config:
            agent.llm_config["tools"] = []
        existing_tool_index = next(
            (index for (index, d) in enumerate(agent.llm_config["tools"]) if d.get("function", {}).get("name") == function.name),
            None
        )

        
        # If it does, update that entry; if not, append a new entry
        if existing_tool_index is not None:
            agent.llm_config["tools"][existing_tool_index] = function_tool_config
        else:
            agent.llm_config["tools"].append(function_tool_config)
        
        # If the function has a class_name, find and register it
        if function.class_name and function.class_name != "":
            class_name, module_name = function.class_name.rsplit(".", 1)
            ServiceClass = FunctionsService._find_class(class_name)
            if ServiceClass is not None:
                method = getattr(ServiceClass, module_name)
                if method is not None:
                    agent.register_function(
                        function_map={
                            function.name: lambda sender, **args: method(sender, **args)
                        }
                    )
                else:
                    return json.dumps({"error": f"Method {module_name} not found in class {class_name}"})
            else:
                return json.dumps({"error": f"Class {class_name} not found"})
        else:
            # For functions without class_name, prepare them for direct execution
            if not function.function_code or function.function_code == "":
                return json.dumps({"error": "function code was empty unexpectedly, either define a class_name or function_code"})
            agent.register_function(
                function_map={
                    function.name: lambda **args: FunctionsService.execute_func(function.function_code, **args)
                }
            )
        return json.dumps({"response": "Function added!"})
    
    @staticmethod
    def _load_json_field(func_spec: Dict[str, Any], field: str) -> Optional[str]:
        from . import OpenAIParameter
        
        # Check if the field is missing
        if field not in func_spec:
            return json.dumps({"error": f"The '{field}' field is missing."})

        field_value = func_spec[field]

        # If the field is already an OpenAIParameter instance or a non-empty dictionary, use it directly
        if isinstance(field_value, OpenAIParameter):
            return None
        elif isinstance(field_value, dict):
            try:
                # Attempt to create an OpenAIParameter instance from a dictionary
                func_spec[field] = OpenAIParameter(**field_value)
                return None
            except ValidationError as e:
                return json.dumps({"error": f"Validation error for '{field}': {str(e)}"})

        # If the field is a non-empty string, attempt to parse it as a JSON string
        elif isinstance(field_value, str) and field_value.strip():
            try:
                parameters_dict = json.loads(field_value)
                func_spec[field] = OpenAIParameter(**parameters_dict)
                return None
            except (json.JSONDecodeError, ValidationError) as e:
                return json.dumps({"error": f"Error parsing JSON for '{field}': {str(e)}"})

        # If the field is none of the above, return an error
        else:
            return json.dumps({"error": f"The '{field}' field must be a JSON string."})

    @staticmethod
    def _create_function_model(agent: GPTAssistantAgent, func_spec: Dict[str, Any]) -> Tuple[Optional[Any], Optional[str]]:
        from . import AddFunctionModel
        # for now only validate parameters through JSON string field, add to this list if other fields come up
        for field in ['parameters']:
            error_message = FunctionsService._load_json_field(func_spec, field)
            if error_message:
                return None, error_message

        try:
            function = AddFunctionModel(**func_spec, auth=agent.auth)
            return function, None
        except ValidationError as e:
            return None, json.dumps({"error": f"Validation error when defining function {func_spec.get('name', '')}: {str(e)}"})

    @staticmethod
    def upsert_function(agent: GPTAssistantAgent, **kwargs: Any) -> str:
        from . import BackendService, AgentService, UpsertAgentModel
        function_model, error_message = FunctionsService._create_function_model(agent, kwargs)
        if error_message:
            return error_message
        err = BackendService.upsert_backend_functions([function_model])
        if err is not None:
            return err

        # update the agent to have the function so it can use it
        agent_upserted, err = AgentService.upsert_agents([UpsertAgentModel(
            auth=agent.auth,
            name=agent.name,
            functions_to_add=[function_model.name],
        )])
        if err is not None:
            return err
        return json.dumps({"response": "Function upserted!"})