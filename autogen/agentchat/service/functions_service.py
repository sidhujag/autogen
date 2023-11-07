        
import json
import sys

from .. import DiscoverableConversableAgent
from typing import List, Any, Optional, Dict, Tuple
from pydantic import ValidationError
from autogen.code_utils import (
    execute_code
)

class FunctionsService:
    @staticmethod
    def discover_functions(sender: DiscoverableConversableAgent, category: str, query: str = None) -> str:
        from . import BackendService, DiscoverFunctionsModel
        response, err = BackendService.discover_backend_functions(DiscoverFunctionsModel(auth=sender.auth, query=query, category=category))
        if err is not None:
            return f"Could not discover functions: {err}"
        return response
    
    @staticmethod
    def execute_func(function_code: str, **args):
        global_vars_code = '\n'.join(f'{key} = {repr(value)}' for key, value in args.items())
        str_code = f"{global_vars_code}{function_code}"
        exitcode, logs, env = execute_code(str_code)
        exitcode2str = "execution succeeded" if exitcode == 0 else "execution failed"
        if logs == "" and exitcode2str == "execution succeeded":
            exitcode2str = "no output found, make sure function uses stdout to output results"
        return f"exitcode: {exitcode} ({exitcode2str})\nCode output: {logs}"

    @staticmethod
    def _find_class(class_name):
        for module in sys.modules.values():
            cls = getattr(module, class_name, None)
            if cls is not None:
                return cls
        return None

    @staticmethod
    def define_function_internal(
        agent: DiscoverableConversableAgent, 
        function
        ) -> str:
        function_config = {
            "name": function.name,
            "description": function.description,
            "parameters": function.parameters.dict(exclude_none=True),
        }
        # Check if a function with the same name already exists
        if 'functions' not in agent.llm_config:
            agent.llm_config["functions"]= []
        existing_function_index = next((index for (index, d) in enumerate(agent.llm_config["functions"]) if d["name"] == function.name), None)
        # If it does, update that entry; if not, append a new entry
        if existing_function_index is not None:
            agent.llm_config["functions"][existing_function_index] = function_config
        else:
            agent.llm_config["functions"].append(function_config)
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
                    return f"Method {module_name} not found in class {class_name}"
            else:
                return f"Class {class_name} not found"
        else:
            if not function.function_code or function.function_code == "":
                return "function code was empty unexpectedly, either define a class_name or function_code"
            agent.register_function(
                function_map={
                    function.name: lambda **args: FunctionsService.execute_func(function.function_code, **args)
                }
            )
            
        return "Function added!"
 
    @staticmethod
    def _load_json_field(func_spec: Dict[str, Any], field: str) -> Optional[str]:
        if field in func_spec and isinstance(func_spec[field], str):
            try:
                func_spec[field] = json.loads(func_spec[field])
            except json.JSONDecodeError as e:
                return f"Error parsing JSON for {field} in function {func_spec.get('name', '')}: {e}"
        return None

    @staticmethod
    def _create_function_model(agent: DiscoverableConversableAgent, func_spec: Dict[str, Any]) -> Tuple[Optional[Any], Optional[str]]:
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
            return None, f"Validation error when defining function {func_spec.get('name', '')}: {e}"

    @staticmethod
    def define_functions(agent: DiscoverableConversableAgent, function_specs: List[Dict[str, Any]]) -> str:
        from . import BackendService
        function_models = []
        function_names = []
        for func_spec in function_specs:
            function, error_message = FunctionsService._create_function_model(agent, func_spec)
            if error_message:
                return error_message
            function_models.append(function)
            function_names.append(function.name)

        err = BackendService.add_backend_functions(function_models)
        if err is not None:
            return f"Could not define functions: {err}"

        return "Functions created or updated! If you want to use the functions now, you may want to add to an agent"

    @staticmethod
    def define_function(agent: DiscoverableConversableAgent, **kwargs: Any) -> str:
        from . import BackendService

        function, error_message = FunctionsService._create_function_model(agent, kwargs)
        if error_message:
            return error_message

        err = BackendService.add_backend_functions([function])
        if err is not None:
            return f"Could not define function: {err}"

        return "Function created or updated! If you want to use the function now, you may want to it add to an agent"