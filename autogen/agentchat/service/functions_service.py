        
import json
from .. import ConversableAgent
from typing import List, Any, Optional, Dict, Tuple
from pydantic import ValidationError
from autogen.code_utils import (
    execute_code
)

class FunctionsService:
    @staticmethod
    def discover_functions(sender: ConversableAgent, category: str, query: str = None) -> str:
        from . import BackendService, DiscoverFunctionsModel
        response, err = BackendService.discover_backend_functions(DiscoverFunctionsModel(auth=sender.auth, query=query, category=category))
        if err is not None:
            return f"Could not discover functions: {err}"
        return response

    @staticmethod
    def add_functions(sender: ConversableAgent, function_names: List[str]) -> str:
        from . import MakeService, UpsertAgentModel
        agent, err = MakeService.upsert_agents([UpsertAgentModel(auth=sender.auth, name=sender.name, function_names=function_names)])
        if err is not None:
            return f"Could not add function(s): {err}"
        return "Function(s) added successfully"

    @staticmethod
    def execute_func(name: str, code: str, packages: List[str], **args):
            package_install_cmd = ' '.join(f'"{pkg}"' for pkg in packages)
            pip_install = f'import subprocess\nsubprocess.run(["pip", "-qq", "install", {package_install_cmd}])' if len(packages) > 0 else ''
            str_code = f"""
        {pip_install}
        print("Result of {name} function execution:")
        {code}
        args={args}
        result={name}(**args)
        if result is not None: print(result)
        """
            print(f"execute_code:\n{str_code}")
            result = execute_code(str_code)[1]
            print(f"Result: {result}")
            return result

    @staticmethod
    def define_function_internal(
        agent: ConversableAgent, 
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
            # Assuming class_name refers to a class with a method named `name`
            agent.register_function(
                function_map={
                    function.name: lambda **args: getattr(globals()[function.class_name](), function.name)(**args)
                }
            )
        else:
            if not function.code or function.code == "":
                return "function code was empty unexpectedly, either define a class_name or code"
            agent.register_function(
                function_map={
                    function.name: lambda **args: FunctionsService.execute_func(function.name, function.code, function.packages or [], **args)
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
    def _create_function_model(agent: ConversableAgent, func_spec: Dict[str, Any]) -> Tuple[Optional[Any], Optional[str]]:
        from . import AddFunctionModel
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
    def define_functions(agent: ConversableAgent, function_specs: List[Dict[str, Any]]) -> str:
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
        
        return FunctionsService.add_functions(agent, function_names)

    @staticmethod
    def define_function(agent: ConversableAgent, **kwargs: Any) -> str:
        from . import BackendService

        function, error_message = FunctionsService._create_function_model(agent, kwargs)
        if error_message:
            return error_message

        err = BackendService.add_backend_functions([function])
        if err is not None:
            return f"Could not define function: {err}"

        return FunctionsService.add_functions(agent, [function.name])