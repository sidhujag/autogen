        
import json
from .. import ConversableAgent
from typing import List, Any
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
    def add_functions(sender: ConversableAgent, function_names: str) -> str:
        from . import MakeService, UpsertAgentModel
        try:
            function_names_list = json.loads(function_names)
            if not isinstance(function_names_list, list):
                return "Error: function_names must be a list"
        except json.JSONDecodeError as e:
            return f"Error parsing JSON when trying to add function: {e}"
        
        agent, err = MakeService.upsert_agent(UpsertAgentModel(auth=sender.auth, name=sender.name, function_names=function_names_list))
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
        if function.class_name and function.class_name is not "":
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
    def define_function(sender: ConversableAgent, **kwargs: Any) -> str:
        from . import BackendService, AddFunctionModel
        # Convert JSON encoded string parameters to dict and list
        if 'parameters' in kwargs and type(kwargs['parameters']) == str:
            try:
                kwargs['parameters'] = json.loads(kwargs['parameters'])
            except json.JSONDecodeError as e:
                return f"Error parsing JSON for parameters: {e}"
        
        if 'packages' in kwargs and type(kwargs['packages']) == str:
            try:
                kwargs['packages'] = json.loads(kwargs['packages'])
            except json.JSONDecodeError as e:
                return f"Error parsing JSON for packages: {e}"

        # Create AddFunctionModel instance
        try:
            function = AddFunctionModel(**kwargs, auth=sender.auth)
        except ValidationError as e:
            return f"Validation error when defining function: {e}"
        # Add the backend function
        err = BackendService.add_backend_function(function)
        if err is not None:
            return f"Could not define function: {err}"
        
        # Convert the function names to a JSON-encoded list of strings and call add_functions
        function_names_json = json.dumps([function.name])
        return FunctionsService.add_functions(sender, function_names_json)