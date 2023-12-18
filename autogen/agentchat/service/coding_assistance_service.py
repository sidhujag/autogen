
from typing import Optional
from aider import models
from aider.coders import Coder
from aider.io import InputOutput
from openai import OpenAI
import json
import requests
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
        from . import MakeService, CodingAssistantInfo, GetCodingAssistantModel, CodeRepositoryService
        backend_coding_assistant = CodingAssistantService.get_coding_assistant(GetCodingAssistantModel(name=name))
        if not backend_coding_assistant:
            return json.dumps({"error": f"Coding assistant({name}) not found"})
        repository_info = CodeRepositoryService.get_code_repository_info(backend_coding_assistant.name)
        if not repository_info:
            return json.dumps({"error": f"Coding repository({backend_coding_assistant.name}) not found"})
        group_description = MakeService._get_short_description(backend_coding_assistant.description)
        # Return the JSON representation of the coding_assistants info
        git_dir = None
        if backend_coding_assistant.repo:
            git_dir = backend_coding_assistant.repo.get_rel_repo_dir()
        backend_coding_assistant_info = CodingAssistantInfo(
            name=name,
            repository_info=repository_info,
            gh_user=MakeService.auth.gh_user,
            description=group_description,
            files=backend_coding_assistant.files,
            git_dir=git_dir,
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
        if err and err != json.dumps({"error": "No coding_assistants were upserted, no changes found!"}):
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
    def _execute_git_command(repo, git_command):
        try:
            result = repo.git.execute(git_command.split())
            return {"response": f"Git command executed successfully: {result}"}
        except repo.git.exc.GitCommandError as e:
            return {"error": f"Error executing Git command: {e}"}

    @staticmethod
    def _create_github_pull_request(token, repo, title, body, head_branch):
        """
        Create a pull request on GitHub, automatically detecting if it's a fork.

        :param token: Personal access token for the GitHub API
        :param repo: Repository name with owner (e.g., "fork-owner/repo")
        :param title: Title of the pull request
        :param body: Content of the pull request
        :param head_branch: Name of the branch where your changes are implemented
        """
        url = f"https://api.github.com/repos/{repo}"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

        # Get repository details to check if it's a fork and find the parent repo
        repo_details = requests.get(url, headers=headers).json()
        if 'parent' in repo_details:
            parent_repo = repo_details['parent']['full_name']  # format: "parent-owner/repo"
            head = f"{repo.split('/')[0]}:{head_branch}"  # format: "fork-owner:branch"
        else:
            parent_repo = repo
            head = head_branch

        # Create the pull request
        pr_url = f"https://api.github.com/repos/{parent_repo}/pulls"
        pr_data = {"title": title, "body": body, "head": head, "base": "main"}
        response = requests.post(pr_url, headers=headers, json=pr_data)
        if response.status_code == 201:
            return {"response": f"Pull request created successfully, URL: {response.json()['html_url']}"}
        else:
            return {"error": f"Failed to create pull request: {response.content}"}

    @staticmethod
    def _create_coding_assistant(backend_coding_assistant):
        from . import MakeService, CodeRepositoryService, GetCodeRepositoryModel, UpsertCodeRepositoryModel
        coder = None
        try:
            code_repository = CodeRepositoryService.get_code_repository(GetCodeRepositoryModel(name=backend_coding_assistant.repository_name))
            if not code_repository:
                return json.dumps({"error": f"Code repository({backend_coding_assistant.name}) not found"})
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
                git_dname=f"coding\{backend_coding_assistant.name}",
                show_diffs=backend_coding_assistant.show_diffs,
                dry_run=backend_coding_assistant.dry_run,
                map_tokens=backend_coding_assistant.map_tokens,
                verbose=backend_coding_assistant.verbose,
            )
            clone_response = CodeRepositoryService.clone_repo(coder.repo, code_repository)
            if isinstance(clone_response, dict) and 'error' in clone_response:
                return json.dumps(clone_response)
            code_repository.associated_code_assistants.add(backend_coding_assistant.name)
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
        command_git_command: Optional[str] = None
    ) -> str:
        from . import GetCodingAssistantModel, UpsertCodingAssistantModel, MakeService
        coder = CodingAssistantService.get_coding_assistant(GetCodingAssistantModel(name=name))
        if coder is None:
            return json.dumps({"error": f"Could not send message to coding_assistant({name}): does not exist."})
        coder.io.console.begin_capture()
        cmd = None
        if command_add:
            coder.commands.cmd_add(command_add)
            cmd = 'add'
            coding_assistants, err = CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
                name=name,
                files=coder.abs_fnames
            )])
            if err is not None:
                return err
        elif command_drop:
            coder.commands.cmd_drop(command_drop)
            cmd = 'drop'
            coding_assistants, err = CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
                name=name,
                files=coder.abs_fnames
            )])
            if err is not None:
                return err
        elif command_clear:
            coder.commands.cmd_clear(None)
            cmd = 'clear'
        elif command_ls:
            coder.commands.cmd_ls(None)
            cmd = 'ls'
        elif command_tokens:
            coder.commands.cmd_tokens(None)
            cmd = 'tokens'
        elif command_undo:
            coder.commands.cmd_undo(None)
            cmd = 'undo'
        elif command_diff:
            coder.commands.cmd_diff(None)
            cmd = 'diff'
        elif command_pull_request:
            pr_title = "Feature: Adding new features by agent"
            pr_body = coder.description
            return json.dumps(CodingAssistantService._create_github_pull_request(MakeService.gh_pat, 
                                                                     f"{MakeService.auth.gh_user}/{coder.repository_name}", 
                                                                     pr_title,
                                                                     pr_body,
                                                                     coder.repo.active_branch))
        elif command_git_command:
            return json.dumps(CodingAssistantService._execute_git_command(coder.repo, command_git_command)) 
        elif command_show_repo_map:
            repo_map = coder.get_repo_map()
            if repo_map:
                coder.io.tool_output(repo_map)
            cmd = 'show_repo_map'
        elif command_apply:
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
            coder.io.tool_output()
            coder.run(with_message=command_message)
        else:
            return json.dumps({"error": "Could not run code assistant, no commands or message provided"})
        str_output = coder.io.console.end_capture()
        return json.dumps({"success": f"Message ({command_message}) was sent and output was: {str_output}"})