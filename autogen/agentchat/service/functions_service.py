        
import json
import sys

from ..contrib.gpt_assistant_agent import GPTAssistantAgent
from typing import List, Any, Optional, Dict, Tuple
from pydantic import ValidationError

from autogen.code_utils import (
    execute_code
)
from ..service.backend_service import BaseFunction
class FunctionsService:
    @staticmethod
    async def get_functions(function_models: List[Any]) -> List[BaseFunction]:
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
            backend_functions, err = await BackendService.get_backend_functions(missing_models)
            if err is None and backend_functions:
                for function in backend_functions:
                    MakeService.FUNCTION_REGISTRY[function.name] = function
                functions.extend(backend_functions)

        return functions

    @staticmethod
    async def test_function(function_name: str, params: Dict[str, Any]) -> str:
        from . import GetFunctionModel, OpenAIParameter
        try:
            # Validate parameters
            OpenAIParameter(**params)
        except ValidationError as e:
            return json.dumps({"error": f"Validation error for params: {str(e)}"})

        # Retrieve the function
        function = await FunctionsService.get_functions([GetFunctionModel(name=function_name)])
        if not function:
            return json.dumps({"error": f"Function({function_name}) not found"})

        # Check for function code
        if not function[0].function_code:
            return json.dumps({"error": f"Function({function_name}) has no function_code"})

        # Execute the function and handle potential errors
        try:
            result = FunctionsService.execute_func(function[0].function_code, **params)
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": f"Error executing function: {str(e)}"})

    @staticmethod
    async def discover_functions(category: str, query: str = None) -> str:
        from . import BackendService, DiscoverFunctionsModel, FunctionsService, GetFunctionModel

        # Fetch the functions from the backend service
        response, err = await BackendService.discover_backend_functions(DiscoverFunctionsModel(query=query, category=category))
        if err is not None:
            return err

        # Flatten the list of lists into a single list of dictionaries
        if isinstance(response, list) and all(isinstance(item, list) for item in response):
            response = [func for sublist in response for func in sublist]
        else:
            return json.dumps({"error": "Invalid response format"})

        # Extract function names from the response
        function_names = [func['name'] for func in response]

        # Prepare GetFunctionModel instances for each function name
        function_models = [GetFunctionModel(name=function_name) for function_name in function_names]

        # Retrieve function statuses
        functions = await FunctionsService.get_functions(function_models)

        # Create a dictionary to map function names to their status
        function_status_map = {func.name: func.status for func in functions if func}

        # Extend the response object with the status of each function
        for func in response:
            func['status'] = function_status_map.get(func['name'], 'not found')

        return json.dumps(response)

    @staticmethod
    async def get_function_info(name: str) -> str:
        from . import GetFunctionModel
        function = await FunctionsService.get_functions([GetFunctionModel(name=name)])
        if not function:
            return json.dumps({"error": f"Function({name}) not found"})
        function[0].auth = None
        return function[0].dict(exclude_none=True)

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
        function_model: BaseFunction
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

        async def async_wrapper(**args):
            return await method(**args)

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
                    # If method is not async, register it directly
                    agent.register_function(
                        function_map={
                            function_model.name: async_wrapper
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
        MakeService.FUNCTION_REGISTRY[function_model.name] = function_model
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
    def _create_function_model(func_spec: Dict[str, Any]) -> Tuple[Optional[BaseFunction], Optional[str]]:
        # for now only validate parameters through JSON string field, add to this list if other fields come up
        for field in ['parameters']:
            error_message = FunctionsService._load_json_field(func_spec, field)
            if error_message:
                return None, error_message

        try:
            function_model = BaseFunction(**func_spec)
            return function_model, None
        except ValidationError as e:
            return None, json.dumps({"error": f"Validation error when defining function {func_spec.get('name', '')}: {str(e)}"})

    @staticmethod
    async def upsert_function(**kwargs: Any) -> str:
        from . import BackendService, MakeService
        function_model, error_message = FunctionsService._create_function_model(kwargs)
        if error_message:
            return error_message
        err = await BackendService.upsert_backend_functions([function_model])
        if err is not None:
            return err
        MakeService.FUNCTION_REGISTRY[function_model.name] = function_model
        return json.dumps({"response": f"Function({function_model.name}) upserted!"})