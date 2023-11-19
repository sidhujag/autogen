        
import json
import sys
import asyncio

from ..contrib.gpt_assistant_agent import GPTAssistantAgent
from typing import List, Any, Optional, Dict, Tuple
from pydantic import ValidationError

from autogen.code_utils import (
    execute_code
)
from ..service.backend_service import BaseFunction
class FunctionsService:
    @staticmethod
    def get_functions(function_models: List[Any]) -> List[BaseFunction]:
        from . import BackendService, MakeService

        functions = []
        missing_models = []

        # First, try to find each function in the registry
        for function_model in function_models:
            function = MakeService.FUNCTION_REGISTRY.get(function_model.name)
            if function:
                functions.append(function)
            else:
                missing_models.append(function_model)

        # If there are missing models, query BackendService
        if missing_models:
            backend_functions, err = BackendService.get_backend_functions(missing_models)
            if err is None and backend_functions:
                for function in backend_functions:
                    MakeService.FUNCTION_REGISTRY[function.name] = function
                functions.extend(backend_functions)

        return functions

    @staticmethod
    def discover_functions(sender: GPTAssistantAgent, category: str, query: str = None) -> str:
        from . import BackendService, DiscoverFunctionsModel, FunctionsService, GetFunctionModel
        response, err = BackendService.discover_backend_functions(DiscoverFunctionsModel(auth=sender.auth, query=query, category=category))
        if err is not None:
            return err

        # Extract function names from the response
        function_names = [func['name'] for func in response]

        # Prepare GetFunctionModel instances for each function name
        function_models = [GetFunctionModel(auth=sender.auth, name=function_name) for function_name in function_names]

        # Retrieve function statuses
        functions = FunctionsService.get_functions(function_models)

        # Create a dictionary to map function names to their status
        function_status_map = {func.name: func.status for func in functions if func}

        # Extend the response object with the status of each function
        for func in response:
            func['status'] = function_status_map.get(func['name'], 'not found')

        return json.dumps(response)

    
    @staticmethod
    def get_function_info(sender: GPTAssistantAgent, name: str) -> str:
        from . import GetFunctionModel
        if sender is None:
            return json.dumps({"error": "Sender not found"})
        function = FunctionsService.get_functions([GetFunctionModel(auth=sender.auth, name=name)])
        if not function:
            return json.dumps({"error": f"Function({name}) not found"})
        return json.dumps({"response": function[0].dict()})

    @staticmethod
    def execute_func(function_code: str, **args):
        global_vars_code = '\n'.join(f'{key} = {repr(value)}' for key, value in args.items())
        str_code = f"{global_vars_code}\n\n{function_code}"
        exitcode, logs, env = execute_code(str_code)
        exit_status = "Execution succeeded" if exitcode == 0 else "Execution failed"

        if logs == "":
            if exitcode == 0:
                return f"No output. Ensure function writes to stdout. Arguments are global variables. Do not run through OpenAI interpreter. Uses local interpreter.\nExit code: {exitcode} ({exit_status})\nArguments: {args}\nFull code:\n```python\n{str_code}\n```"
            else:
                return f"Function execution error! Fix the code using upsert_function. Arguments are global variables. Do not run through OpenAI interpreter. Uses local interpreter.\nExit code: {exitcode} ({exit_status})\nLogs: '{logs}'\nArguments: {args}\nFull code:\n```python\n{str_code}\n```"

        return f"Exit code: {exitcode} ({exit_status})\nLogs: '{logs}'. Update code if results are unexpected. Arguments are global variables. Do not run through OpenAI interpreter. Uses local interpreter.\nArguments: {args}\nFull code:\n```python\n{str_code}\n```"

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
        function_model
    ) -> str:
        from . import MakeService, OpenAIParameter
        function_model.parameters = function_model.parameters or OpenAIParameter()
        
        # Prepare the function tool configuration
        function_tool_config = {
            "type": "function",
            "function": {
                "name": function_model.name,
                "description": function_model.description,
                "parameters": function_model.parameters.dict(exclude_none=True)
            }
        }
        
        # Check if a tool with the same name already exists
        if 'tools' not in agent.llm_config:
            agent.llm_config["tools"] = []
        existing_tool_index = next(
            (index for (index, d) in enumerate(agent.llm_config["tools"]) if d.get("function", {}).get("name") == function_model.name),
            None
        )

        
        # If it does, update that entry; if not, append a new entry
        if existing_tool_index is not None:
            agent.llm_config["tools"][existing_tool_index] = function_tool_config
        else:
            agent.llm_config["tools"].append(function_tool_config)
        
        # If the function has a class_name, find and register it
        if function_model.class_name and function_model.class_name != "":
            class_name, module_name = function_model.class_name.rsplit(".", 1)
            ServiceClass = FunctionsService._find_class(class_name)
            if ServiceClass is not None:
                method = getattr(ServiceClass, module_name)
                if method is not None:
                    if asyncio.coroutines.iscoroutinefunction(method):
                        # If method is async, define a wrapper to run it synchronously
                        def sync_wrapper(sender, **args):
                            return asyncio.run(method(sender, **args))
                        agent.register_function(
                            function_map={
                                function_model.name: sync_wrapper
                            }
                        )
                    else:
                        # If method is not async, register it directly
                        agent.register_function(
                            function_map={
                                function_model.name: lambda sender, **args: method(sender, **args)
                            }
                        )
                else:
                    return json.dumps({"error": f"Method {module_name} not found in class {class_name}"})
            else:
                return json.dumps({"error": f"Class {class_name} not found"})
        else:
            # For functions without class_name, prepare them for direct execution
            if not function_model.function_code or function_model.function_code == "":
                return json.dumps({"error": "function code was empty unexpectedly, either define a class_name or function_code"})
            agent.register_function(
                function_map={
                    function_model.name: lambda **args: FunctionsService.execute_func(function_model.function_code, **args)
                }
            )
        MakeService.FUNCTION_REGISTRY[function_model.name] = BaseFunction(**function_model.dict(exclude_none=True))
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
        # If the field is none of the above, return an error
        else:
            return json.dumps({"error": f"The '{field}' field must be a dictonary."})

    @staticmethod
    def _create_function_model(agent: GPTAssistantAgent, func_spec: Dict[str, Any]) -> Tuple[Optional[Any], Optional[str]]:
        from . import AddFunctionModel
        # for now only validate parameters through JSON string field, add to this list if other fields come up
        for field in ['parameters']:
            error_message = FunctionsService._load_json_field(func_spec, field)
            if error_message:
                return None, error_message

        try:
            function_model = AddFunctionModel(**func_spec, auth=agent.auth)
            if function_model.function_code:
                function_model.last_updater = agent.name
            return function_model, None
        except ValidationError as e:
            return None, json.dumps({"error": f"Validation error when defining function {func_spec.get('name', '')}: {str(e)}"})

    @staticmethod
    def upsert_function(sender: GPTAssistantAgent, **kwargs: Any) -> str:
        from . import BackendService, AgentService, UpsertAgentModel, MakeService
        function_model, error_message = FunctionsService._create_function_model(sender, kwargs)
        if error_message:
            return error_message
        err = BackendService.upsert_backend_functions([function_model])
        if err is not None:
            return err
        # update the agent to have the function so it can use it
        agent_upserted, err = AgentService.upsert_agents([UpsertAgentModel(
            auth=sender.auth,
            name=sender.name,
            functions_to_add=[function_model.name],
        )])
        if err is not None:
            return err
        MakeService.FUNCTION_REGISTRY[function_model.name] = BaseFunction(**function_model.dict(exclude_none=True))
        return json.dumps({"response": "Function upserted!"})