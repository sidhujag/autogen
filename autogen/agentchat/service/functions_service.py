        
import json
from .. import MakeService, BackendService, ConversableAgent
from backend_service import AddFunctionModel, DiscoverFunctionsModel
from typing import Dict, List, Union
from autogen.code_utils import (
    execute_code
)

class FunctionsService:
    def discover_functions(self, sender: ConversableAgent, category: str, query: str = None) -> str:
        # Assume the FastAPI endpoint is /discover_functions
        response, err = BackendService.discover_functions(sender, DiscoverFunctionsModel(query=query, category=category))
        if err is not None:
            return f"Could not discover functions: {err}"
        return response

    def add_functions(self, sender: ConversableAgent, function_names: str) -> str:
        try:
            json_fns = json.loads(function_names)
        except json.JSONDecodeError as e:
            return f"Error parsing JSON when trying to add function: {e}"
        # function_names is cumulatively added
        response, err = MakeService.upsert_agent(sender, {"name": sender.name, "function_names": json_fns})
        if err is not None:
            return f"Could not add function(s): {err}"
        return "Functions added successfully"

    def execute_func(self, name: str, code: str, packages: List[str], **args):
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

    def define_function_internal(
        self,
        agent, 
        name: str, 
        description: str, 
        json_args: Dict[str, Union[str, Dict]],
        code: str, 
        json_reqs: List[str],
        packages: List[str],
        class_name: str = None
        ) -> str:
        function_config = {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": json_args},
            "required": json_reqs,
        }
        # Check if a function with the same name already exists
        existing_function_index = next((index for (index, d) in enumerate(agent.llm_config["functions"]) if d["name"] == name), None)
        # If it does, update that entry; if not, append a new entry
        if existing_function_index is not None:
            agent.llm_config["functions"][existing_function_index] = function_config
        else:
            agent.llm_config["functions"].append(function_config)
        if class_name:
            # Assuming class_name refers to a class with a method named `name`
            agent.register_function(
                function_map={
                    name: lambda **args: getattr(globals()[class_name](), name)(**args)
                }
            )
        else:
            agent.register_function(
                function_map={
                    name: lambda **args: self.execute_func(name, code, packages, **args)
                }
            )
        return f"A function has been added to the context of this agent.\nDescription: {description}"
 
    def define_function(
        self,
        sender: ConversableAgent,
        name: str,
        description: str,
        category: str,
        code: str,
        arguments: str = None,
        required_arguments: str = None,
        packages: str = None
    ) -> str:
        json_args = None
        json_reqs = None
        package_list = None
        try:
            if arguments:
                json_args = json.loads(arguments)
            if required_arguments:
                json_reqs = json.loads(required_arguments)
            if packages:
                package_list = json.loads(packages)
        except json.JSONDecodeError as e:
            return f"Error parsing JSON when defining function: {e}"
        
        result, err = BackendService.add_function(sender, AddFunctionModel(
            name=name,
            description=description,
            required=json_reqs,
            arguments=json_args,
            packages=package_list,
            code=code,
            category=category
        ))
        if err is not None:
            return f"Could not define function: {err}"
        
        return self.add_functions(sender, json.dumps([name]))