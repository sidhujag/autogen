
from typing import Optional
from aider import models
from aider.coders import Coder
from aider.io import InputOutput
from openai import OpenAI
import json
import logging
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from pathlib import Path

class CodingAssistantService:
    @staticmethod
    async def get_coding_assistant(coding_assistant_model) -> Coder:
        from . import BackendService, MakeService, DeleteCodeAssistantsModel
        coding_assistant: Coder = MakeService.CODE_ASSISTANT_REGISTRY.get(coding_assistant_model.name)
        if coding_assistant is None:
            backend_coding_assistants, err = await BackendService.get_backend_coding_assistants([coding_assistant_model])
            if err is None and backend_coding_assistants:
                coding_assistant, err = await CodingAssistantService.make_coding_assistant(backend_coding_assistants[0])
                if err is None and coding_assistant:
                    MakeService.CODE_ASSISTANT_REGISTRY[coding_assistant_model.name] = coding_assistant
                else:
                    await BackendService.delete_backend_coding_assistants([DeleteCodeAssistantsModel(name=coding_assistant_model.name)])
        return coding_assistant
    
    @staticmethod
    async def get_coding_assistant_info(name: str) -> str:
        from . import MakeService, CodingAssistantInfo, CodeRepositoryInfo, GetCodingAssistantModel, CodeRepositoryService
        backend_coding_assistant = await CodingAssistantService.get_coding_assistant(GetCodingAssistantModel(name=name))
        if not backend_coding_assistant:
            return json.dumps({"error": f"Coding assistant({name}) not found"})
        repository_info_result = await CodeRepositoryService.get_code_repository_info(backend_coding_assistant.repository_name)
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
    async def discover_coding_assistants(query: str) -> str:
        from . import BackendService, DiscoverCodingAssistantModel
        response, err = await BackendService.discover_backend_coding_assistants(DiscoverCodingAssistantModel(query=query))
        if err is not None:
            return err
        return response

    @staticmethod
    async def upsert_coding_assistant(
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
        coding_assistants, err = await CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
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
    async def make_coding_assistant(backend_coding_assistant):
        from . import MakeService
        coding_assistant, err = await CodingAssistantService._create_coding_assistant(backend_coding_assistant)
        if err is not None:
            return None, err
        coding_assistant.description = backend_coding_assistant.description
        coding_assistant.model = backend_coding_assistant.model
        coding_assistant.repository_name = backend_coding_assistant.repository_name
        coding_assistant.name = backend_coding_assistant.name
        coding_assistant.files = backend_coding_assistant.files
        coding_assistant.show_diffs = backend_coding_assistant.show_diffs
        coding_assistant.dry_run = backend_coding_assistant.dry_run
        coding_assistant.map_tokens = backend_coding_assistant.map_tokens
        coding_assistant.verbose = backend_coding_assistant.verbose
        MakeService.CODE_ASSISTANT_REGISTRY[coding_assistant.name] = coding_assistant
        return coding_assistant, None

    @staticmethod
    async def upsert_coding_assistants(upsert_models):
        from . import BackendService, GetCodingAssistantModel
        # Step 1: Upsert all coding_assistants in batch
        err = await BackendService.upsert_backend_coding_assistants(upsert_models)
        if err and err != json.dumps({"error": "No coding assistants were upserted, no changes found!"}):
            return None, err
        # Step 2: Retrieve all coding assistants from backend in batch
        get_coding_assistant_models = [GetCodingAssistantModel(name=model.name) for model in upsert_models]
        backend_coding_assistants, err = await BackendService.get_backend_coding_assistants(get_coding_assistant_models)
        if err:
            return None, err
        if len(backend_coding_assistants) == 0:
            return None, json.dumps({"error": "Could not fetch coding_assistants from backend"})

        # Step 3: Update local coding_assistant registry
        successful_coding_assistants = []
        for backend_coding_assistant in backend_coding_assistants:
            coder, err = await CodingAssistantService.make_coding_assistant(backend_coding_assistant)
            if err is not None:
                return None, err
            successful_coding_assistants.append(coder)
        return successful_coding_assistants, None

    @staticmethod
    async def _create_coding_assistant(backend_coding_assistant):
        from . import MakeService, CodeRepositoryService, GetCodeRepositoryModel, UpsertCodeRepositoryModel
        coder = None
        try:
            code_repository = await CodeRepositoryService.get_code_repository(GetCodeRepositoryModel(name=backend_coding_assistant.repository_name))
            if not code_repository:
                return None, json.dumps({"error": f"Code repository({backend_coding_assistant.repository_name}) not found"})
            io = InputOutput(pretty=False, yes=True, input_history_file=f".aider.input.history-{backend_coding_assistant.name}", chat_history_file=f".aider.chat.history-{backend_coding_assistant.name}.md")
            client = OpenAI(api_key=MakeService.auth.api_key)
            main_model = models.Model.create(backend_coding_assistant.model or "gpt-4-turbo-preview", client)
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
            coder.last_processed_index = -1
            coder.commands.cmd_add("docs/**/*")
            if backend_coding_assistant.name not in code_repository.associated_code_assistants:
                code_repository.associated_code_assistants.append(backend_coding_assistant.name)

            coding_assistants, err = await CodeRepositoryService.upsert_code_repositories([UpsertCodeRepositoryModel(
                name=code_repository.name,
                associated_code_assistants=code_repository.associated_code_assistants
            )])
            if err is not None:
                return None, err
        except ValueError as err:
            return None, str(err)
        return coder, None

    @staticmethod
    async def run_code_assistant(coder, code_repository, command_message: str):
        try:
            coder.io.add_to_input_history(command_message)
            coder.io.tool_output()
            coder.run(with_message=command_message)
            msgs = coder.done_messages + coder.cur_messages
            new_messages = msgs[coder.last_processed_index + 1 :]
            if new_messages:
                coder.last_processed_index = len(msgs) - 1
            return new_messages
        except Exception as e:
            print(f'run_code_assistant exec {str(e)}')
            return None

    @staticmethod
    def read_text(file_path: str) -> tuple[str, Optional[str]]:
        try:
            with open(file_path, 'r') as file:
                text = file.read()
            return text, None
        except Exception as e:
            return None, json.dumps({"error": str(e)})

    @staticmethod
    def show_file(command_show_file: str, workspace: Path):
        # Construct the full path of the file within the workspace
        full_file_path = workspace / command_show_file

        # Check if the file path is within the workspace directory
        if not full_file_path.is_absolute() or not full_file_path.resolve().is_relative_to(workspace):
            return None, json.dumps({"error": "File path is outside the workspace directory."})

        # Read and return the file content if it is within the workspace
        text, err = CodingAssistantService.read_text(str(full_file_path))
        if err is not None:
            return None, err
        return text, None
        
    @staticmethod
    async def manage_coding_assistant(
        name: Optional[str] = None,
        command_show_repo_map: Optional[bool] = None,
        command_clear: Optional[bool] = None,
        command_ls: Optional[bool] = None,
        command_undo: Optional[bool] = None,
        command_diff: Optional[bool] = None,
        command_git_command: Optional[str] = None,
        command_show_file: Optional[str] = None
    ) -> str:
        from . import GroupService, GetGroupModel, UpsertGroupModel, CodeExecInput, CodeRepositoryService, GetCodeRepositoryModel, GetCodingAssistantModel, UpsertCodingAssistantModel, BackendService
        # Wait for any previous task to complete
        current_group = await GroupService.get_group(GetGroupModel(name=GroupService.current_group_name))
        if current_group is None:
            return json.dumps({"error": f"Could not send message: current_group({GroupService.current_group_name}) not found"})
        if current_group.code_assistance_event_task:
            return json.dumps({"error": "Code assistant is currently running, please wait for it to finish before sending another command."})
        name = name or current_group.current_code_assistant_name
        coder = await CodingAssistantService.get_coding_assistant(GetCodingAssistantModel(name=name))
        if coder is None:
            return json.dumps({"error": f"Critical: Could not send message to coding_assistant({name}): does not exist. Check the name or make sure you have created one first."})
        code_repository = await CodeRepositoryService.get_code_repository(GetCodeRepositoryModel(name=coder.repository_name))
        if not code_repository:
            return json.dumps({"error": f"Critical: Associated code repository({coder.repository_name}) not found."})
        if current_group.current_code_assistant_name != name:
            group_managers, err = await GroupService.upsert_groups([UpsertGroupModel(
                name=current_group.name,
                current_code_assistant_name=name,
            )])
            if err is not None:
                return err
        str_output = ''
        cmd = None
        if command_clear:
            logging.info("manage_coding_assistant cmd_clear")
            coder.io.console.begin_capture()
            coder.commands.cmd_clear(None)
            cmd = 'command_clear'
            coder.last_processed_index = -1
        elif command_ls:
            logging.info("manage_coding_assistant command_ls")
            coder.io.console.begin_capture()
            coder.commands.cmd_ls(None)
            cmd = 'command_ls'
        elif command_undo:
            logging.info("manage_coding_assistant command_undo")
            coder.io.console.begin_capture()
            coder.commands.cmd_undo(None)
            cmd = 'command_undo'
        elif command_diff:
            logging.info("manage_coding_assistant command_diff")
            coder.io.console.begin_capture()
            coder.commands.cmd_diff(None)
            cmd = 'command_diff'
        elif command_git_command:
            logging.info(f"manage_coding_assistant command_git_command {command_git_command}")
            response, err = await BackendService.execute_git_command(CodeExecInput(
                workspace=code_repository.workspace,
                command_git_command=command_git_command,
            ))
            if err is not None:
                logging.error(f"command_git_command failed: {err}")
                return err
            return response
        elif command_show_repo_map:
            logging.info("manage_coding_assistant command_show_repo_map")
            coder.io.console.begin_capture()
            repo_map = coder.get_repo_map()
            if repo_map:
                coder.io.tool_output(repo_map)
            cmd = 'command_show_repo_map'
        elif command_show_file:
            logging.info(f"manage_coding_assistant command_show_file {command_show_file}")
            text, err = CodingAssistantService.show_file(command_show_file, Path(code_repository.workspace))
            if err is not None:
                logging.error(f"command_show_file failed: {err}")
                return err
            return text
        else:
            return json.dumps({"error": "Could not manage code assistant, no commands or message provided"})

        str_output = coder.io.console.end_capture()
        return json.dumps({"success": f"{cmd}: {str_output}"})

    @staticmethod
    async def run_coding_assistant(
        query: str,
        name: Optional[str] = None,
    ) -> str:
        from . import GroupService, GetGroupModel, UpsertGroupModel, CodeRepositoryService, GetCodeRepositoryModel, GetCodingAssistantModel, UpsertCodingAssistantModel, BackendService
        # Wait for any previous task to complete
        current_group = await GroupService.get_group(GetGroupModel(name=GroupService.current_group_name))
        if current_group is None:
            return json.dumps({"error": f"Could not send message: current_group({GroupService.current_group_name}) not found"})
        if current_group.code_assistance_event_task:
            return json.dumps({"error": "Code assistant is currently running, please wait for it to finish before sending another command."})
        name = name or current_group.current_code_assistant_name
        coder = await CodingAssistantService.get_coding_assistant(GetCodingAssistantModel(name=name))
        if coder is None:
            return json.dumps({"error": f"Critical: Could not send message to coding_assistant({name}): does not exist. Check the name or make sure you have created one first."})
        code_repository = await CodeRepositoryService.get_code_repository(GetCodeRepositoryModel(name=coder.repository_name))
        if not code_repository:
            return json.dumps({"error": f"Critical: Associated code repository({coder.repository_name}) not found."})
        if current_group.current_code_assistant_name != name:
            group_managers, err = await GroupService.upsert_groups([UpsertGroupModel(
                name=current_group.name,
                current_code_assistant_name=name,
            )])
            if err is not None:
                return err
        logging.info(f"run_coding_assistant command_message {query}")
        # cancel any assistant run so we can get group chat to run the code assistant
        GPTAssistantAgent.cancel_run("Running coding assistant, waiting on results...")

        # Wrapper function for starting the code assistance task
        def setup_code_assistance_event_task():
            async def start_task():
                return await GroupService.start_code_assistance_task(
                    CodingAssistantService.run_code_assistant,
                    GroupService.process_code_assistance_results,
                    coder,
                    code_repository,
                    query
                )
            return start_task

        current_group.code_assistance_event_task = setup_code_assistance_event_task()
        return json.dumps({"success": "Ran coding assistant. Please wait for results."})
    
    