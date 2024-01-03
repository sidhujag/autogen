
from typing import Optional
from aider import models
from aider.coders import Coder
from aider.io import InputOutput
from openai import OpenAI
import json


class CodingAssistantService:
    @staticmethod
    def get_coding_assistant(coding_assistant_model) -> Coder:
        from . import BackendService, MakeService
        coding_assistant: Coder = MakeService.CODE_ASSISTANT_REGISTRY.get(coding_assistant_model.name)
        if coding_assistant is None:
            backend_coding_assistants, err = BackendService.get_backend_coding_assistants([coding_assistant_model])
            if err is None and backend_coding_assistants:
                coding_assistant, err = CodingAssistantService.make_coding_assistant(backend_coding_assistants[0])
                if err is None and coding_assistant:
                    MakeService.CODE_ASSISTANT_REGISTRY[coding_assistant_model.name] = coding_assistant
        return coding_assistant
    
    @staticmethod
    def get_coding_assistant_info(name: str) -> str:
        from . import MakeService, CodingAssistantInfo, CodeRepositoryInfo, GetCodingAssistantModel, CodeRepositoryService
        backend_coding_assistant = CodingAssistantService.get_coding_assistant(GetCodingAssistantModel(name=name))
        if not backend_coding_assistant:
            return json.dumps({"error": f"Coding assistant({name}) not found"})
        repository_info_result = CodeRepositoryService.get_code_repository_info(backend_coding_assistant.repository_name)
        repository_info_json = json.loads(repository_info_result)
        if 'error' in repository_info_json:
            return repository_info_json
        
        # Deserialize the JSON string to a Python dictionary
        repository_info_dict = repository_info_json["response"]

        # Create a CodeRepositoryInfo object from the dictionary
        repository_info = CodeRepositoryInfo(**repository_info_dict)
        group_description = MakeService._get_short_description(backend_coding_assistant.description)
        backend_coding_assistant_info = CodingAssistantInfo(
            name=name,
            repository_info=repository_info,
            gh_user=MakeService.auth.gh_user,
            description=group_description,
            files=backend_coding_assistant.files,
            model=backend_coding_assistant.model,
            show_diffs=backend_coding_assistant.show_diffs,
            dry_run=backend_coding_assistant.dry_run,
            map_tokens=backend_coding_assistant.map_tokens,
            verbose=backend_coding_assistant.verbose
        )
        return json.dumps({"response": backend_coding_assistant_info.dict()})

    @staticmethod
    def discover_coding_assistants(query: str) -> str:
        from . import BackendService, DiscoverCodingAssistantModel
        response, err = BackendService.discover_backend_coding_assistants(DiscoverCodingAssistantModel(query=query))
        if err is not None:
            return err
        return response

    @staticmethod
    def upsert_coding_assistant(
        name: str,
        repository_name: str,
        description: Optional[str] = None,
        model: Optional[str] = None,
        show_diffs: Optional[bool] = None,
        dry_run: Optional[bool] = None,
        map_tokens: Optional[int] = None,
        verbose: Optional[bool] = None,
    ) -> str:
        from . import UpsertCodingAssistantModel
        coding_assistants, err = CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
            repository_name=repository_name,
            name=name,
            description=description,
            model=model,
            show_diffs=show_diffs,
            dry_run=dry_run,
            map_tokens=map_tokens,
            verbose=verbose
        )])
        if err is not None:
            return err
        return json.dumps({"response": f"Coding assistant({name}) upserted!"})

    @staticmethod
    def make_coding_assistant(backend_coding_assistant):
        from . import MakeService
        coding_assistant, err = CodingAssistantService._create_coding_assistant(backend_coding_assistant)
        if err is not None:
            return None, err
        coding_assistant.description = backend_coding_assistant.description
        coding_assistant.model = backend_coding_assistant.model
        coding_assistant.repository_name = backend_coding_assistant.repository_name
        coding_assistant.name = backend_coding_assistant.name
        coding_assistant.files = backend_coding_assistant.files,
        coding_assistant.show_diffs = backend_coding_assistant.show_diffs,
        coding_assistant.dry_run = backend_coding_assistant.dry_run,
        coding_assistant.map_tokens = backend_coding_assistant.map_tokens,
        coding_assistant.verbose = backend_coding_assistant.verbose
        MakeService.CODE_ASSISTANT_REGISTRY[coding_assistant.name] = coding_assistant
        return coding_assistant, None

    @staticmethod
    def upsert_coding_assistants(upsert_models):
        from . import BackendService, GetCodingAssistantModel
        # Step 1: Upsert all coding_assistants in batch
        err = BackendService.upsert_backend_coding_assistants(upsert_models)
        if err and err != json.dumps({"error": "No coding assistants were upserted, no changes found!"}):
            return None, err
        # Step 2: Retrieve all coding assistants from backend in batch
        get_coding_assistant_models = [GetCodingAssistantModel(name=model.name) for model in upsert_models]
        backend_coding_assistants, err = BackendService.get_backend_coding_assistants(get_coding_assistant_models)
        if err:
            return None, err
        if len(backend_coding_assistants) == 0:
            return None, json.dumps({"error": "Could not fetch coding_assistants from backend"})

        # Step 3: Update local coding_assistant registry
        successful_coding_assistants = []
        for backend_coding_assistant in backend_coding_assistants:
            coder, err = CodingAssistantService.make_coding_assistant(backend_coding_assistant)
            if err is not None:
                return None, err
            successful_coding_assistants.append(coder)
        return successful_coding_assistants, None

    @staticmethod
    def _create_coding_assistant(backend_coding_assistant):
        from . import MakeService, CodeRepositoryService, GetCodeRepositoryModel, UpsertCodeRepositoryModel
        coder = None
        try:
            code_repository = CodeRepositoryService.get_code_repository(GetCodeRepositoryModel(name=backend_coding_assistant.repository_name))
            if not code_repository:
                return None, json.dumps({"error": f"Code repository({backend_coding_assistant.repository_name}) not found"})
            io = InputOutput(pretty=False, yes=True, input_history_file=f".aider.input.history-{backend_coding_assistant.name}", chat_history_file=f".aider.chat.history-{backend_coding_assistant.name}.md")
            client = OpenAI(api_key=MakeService.auth.api_key)
            main_model = models.Model.create(backend_coding_assistant.model or "gpt-4-1106-preview", client)
            coder = Coder.create(
                main_model=main_model,
                edit_format=None,
                io=io,
                skip_model_availabily_check=False,
                client=client,
                ##
                fnames=backend_coding_assistant.files,
                git_dname=code_repository.workspace,
                show_diffs=backend_coding_assistant.show_diffs,
                dry_run=backend_coding_assistant.dry_run,
                map_tokens=backend_coding_assistant.map_tokens,
                verbose=backend_coding_assistant.verbose,
            )
            if backend_coding_assistant.name not in code_repository.associated_code_assistants:
                code_repository.associated_code_assistants.append(backend_coding_assistant.name)

            coding_assistants, err = CodeRepositoryService.upsert_code_repositories([UpsertCodeRepositoryModel(
                name=code_repository.name,
                associated_code_assistants=code_repository.associated_code_assistants
            )])
            if err is not None:
                return None, err
        except ValueError as err:
            return None, str(err)
        return coder, None

    @staticmethod
    def send_message_to_coding_assistant(
        name: str,
        assistant_type:  Optional[str] = None,
        command_pull_request: Optional[bool] = None,
        command_apply: Optional[str] = None,
        command_show_repo_map: Optional[bool] = None,
        command_message: Optional[str] = None,
        command_add: Optional[str] = None,
        command_drop: Optional[str] = None,
        command_clear: Optional[bool] = None,
        command_ls: Optional[bool] = None,
        command_tokens: Optional[bool] = None,
        command_undo: Optional[bool] = None,
        command_diff: Optional[bool] = None,
        command_git_command: Optional[str] = None,
        command_create_test_for_file: Optional[str] = None
    ) -> str:
        from . import CodeExecInput, CodeRequestInput, CodeRepositoryService, CodeAssistantInput, GetCodeRepositoryModel, GetCodingAssistantModel, UpsertCodingAssistantModel, BackendService
        coder = CodingAssistantService.get_coding_assistant(GetCodingAssistantModel(name=name))
        if coder is None:
            return json.dumps({"error": f"Could not send message to coding_assistant({name}): does not exist."})
        code_repository = CodeRepositoryService.get_code_repository(GetCodeRepositoryModel(name=coder.repository_name))
        if not code_repository:
            return json.dumps({"error": f"Associated code repository({coder.repository_name}) not found"})
        str_output = ''
        reqa_file = None
        cmd = None
        if command_create_test_for_file:
            if not command_message:
                return json.dumps({"error": "Please provide command_message as natural language description of task for code coverage."})
            reqa_file=command_create_test_for_file
            assistant_type="metagpt"
        elif command_add:
            coder.io.console.begin_capture()
            coder.commands.cmd_add(command_add)
            cmd = 'add'
            coding_assistants, err = CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
                name=name,
                files=list(coder.abs_fnames)
            )])
            if err is not None:
                return err
        elif command_drop:
            coder.io.console.begin_capture()
            coder.commands.cmd_drop(command_drop)
            cmd = 'drop'
            coding_assistants, err = CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
                name=name,
                files=list(coder.abs_fnames)
            )])
            if err is not None:
                return err
        elif command_clear:
            coder.io.console.begin_capture()
            coder.commands.cmd_clear(None)
            cmd = 'clear'
        elif command_ls:
            coder.io.console.begin_capture()
            coder.commands.cmd_ls(None)
            cmd = 'ls'
        elif command_tokens:
            coder.io.console.begin_capture()
            coder.commands.cmd_tokens(None)
            cmd = 'tokens'
        elif command_undo:
            coder.io.console.begin_capture()
            coder.commands.cmd_undo(None)
            cmd = 'undo'
        elif command_diff:
            coder.io.console.begin_capture()
            coder.commands.cmd_diff(None)
            cmd = 'diff'
        elif command_pull_request:
            pr_title = "Feature: Adding new features by agent"
            pr_body = coder.description
            response, err = BackendService.create_github_pull_request(CodeRequestInput(
                repository_name=coder.repository_name,
                title=pr_title,
                body=pr_body,
                branch=coder.repo.active_branch
            ))
            if err is not None:
                return err
            return response
        elif command_git_command:
            response, err = BackendService.execute_git_command(CodeExecInput(
                workspace=code_repository.workspace,
                command_git_command=command_git_command,
            ))
            if err is not None:
                return err
            return response
        elif command_show_repo_map:
            coder.io.console.begin_capture()
            repo_map = coder.get_repo_map()
            if repo_map:
                coder.io.tool_output(repo_map)
            cmd = 'show_repo_map'
        elif command_apply:
            coder.io.console.begin_capture()
            content = coder.io.read_text(command_apply)
            if content is None:
                str_output = coder.io.console.end_capture()
                return json.dumps({"error":f"Command ({cmd}) could not be sent, output was: {str_output}"})
            coder.partial_response_content = content
            coder.apply_updates()
            cmd = 'apply'
        if cmd is not None:
            str_output = coder.io.console.end_capture()
            return json.dumps({"success": f"Command ({cmd}) ran and output was: {str_output}"})
        if command_message:
            if assistant_type == "metagpt":
                response, err = BackendService.run_code_assistant(CodeAssistantInput(
                    workspace=code_repository.workspace,
                    project_name=coder.repository_name,
                    command_message=command_message,
                    reqa_file=reqa_file
                ))
                if err is not None:
                    return err
                str_output = response
            elif assistant_type == "aider":
                coder.io.tool_output()
                coder.run(with_message=command_message)
                str_output = coder.io.console.end_capture()
            else:
                return json.dumps({"error":f"assistant_type not provided, must be either 'metagpt' or 'aider'"})
        else:
            return json.dumps({"error": "Could not run code assistant, no commands or message provided"})
        return json.dumps({"success": f"Message ({command_message}) was sent and output was: {str_output}"})