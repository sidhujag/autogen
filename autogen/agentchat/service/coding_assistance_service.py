
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
        coding_assistant: Coder = MakeService.CODE_ASSISTANT_REGISTRY.get(coding_assistant_model.gh_remote_url)
        if coding_assistant is None:
            backend_coding_assistants, err = BackendService.get_backend_coding_assistants([coding_assistant_model])
            if err is None and backend_coding_assistants:
                coding_assistant, err = CodingAssistantService.make_coding_assistant(backend_coding_assistants[0])
                if err is None and coding_assistant:
                    MakeService.CODE_ASSISTANT_REGISTRY[coding_assistant_model.gh_remote_url] = coding_assistant
        return coding_assistant
    
    @staticmethod
    def get_coding_assistant_info(gh_remote_url: str) -> str:
        from . import MakeService, CodingAssistantInfo, GetCodingAssistantModel
        backend_coding_assistant = CodingAssistantService.get_coding_assistant(GetCodingAssistantModel(auth=MakeService.auth, gh_remote_url=gh_remote_url))
        if not backend_coding_assistant:
            return json.dumps({"error": f"Coding assistant(repository: {gh_remote_url}) not found"})
        group_description = MakeService._get_short_description(backend_coding_assistant.description)
        # Return the JSON representation of the coding_assistants info
        git_dir = None
        if backend_coding_assistant.repo:
            git_dir = backend_coding_assistant.repo.get_rel_repo_dir()
        backend_coding_assistant_info = CodingAssistantInfo(
            gh_remote_url=backend_coding_assistant.gh_remote_url,
            gh_user=MakeService.auth.gh_user,
            description=group_description,
            files=backend_coding_assistant.abs_fnames,
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
        from . import BackendService, DiscoverCodingAssistantModel, MakeService
        response, err = BackendService.discover_backend_coding_assistants(DiscoverCodingAssistantModel(auth=MakeService.auth, query=query))
        if err is not None:
            return err
        return response

    @staticmethod
    def _create_github_repository(token, name, description="", private=False):
        """
        Create a new GitHub repository.

        :param token: Personal access token for the GitHub API
        :param name: Name of the repository
        :param description: Description of the repository
        :param private: Boolean indicating whether the repository is private
        """
        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "name": name,
            "description": description,
            "private": private
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return json.dumps({"response": f"Repository ({name}) created successfully!"})
        elif response.status_code == 422:
            return json.dumps({"response": f"Repository ({name}) already exists!"})
        else:
            return json.dumps({"error": f"Failed to create repository: {response.json()}"})

    @staticmethod
    def create_github_remote_repo(
        repository_name: str,
        description: Optional[str] = "",
        private: Optional[bool] = False
    ) -> str:
        from . import MakeService
        return CodingAssistantService._create_github_repository(MakeService.auth.gh_pat, repository_name, description, private)

    @staticmethod
    def _construct_github_remote_url(gh_user, gh_pat, gh_remote_url):
        """
        Embed the GitHub username and PAT into the GitHub remote URL.

        :param gh_user: GitHub username
        :param gh_pat: GitHub Personal Access Token
        :param gh_remote_url: Original GitHub remote URL
        :return: GitHub remote URL with embedded username and PAT
        """
        # Split the original URL to insert username and PAT
        url_parts = gh_remote_url.split('://')
        if len(url_parts) != 2 or not url_parts[1].startswith("github.com"):
            raise ValueError("Invalid GitHub remote URL")

        # Construct the new URL with username and PAT
        new_url = f"https://{gh_user}:{gh_pat}@{url_parts[1]}"
        return new_url

    @staticmethod
    def _is_repo_cloned(repo, remote_url):
        """
        Check if the GitPython Repo object is associated with the given remote URL.

        :param repo: GitPython Repo object
        :param remote_url: URL of the remote repository to check
        :return: True if the Repo is cloned from the remote URL, False otherwise
        """
        try:
            for remote in repo.remotes:
                for url in remote.urls:
                    if url == remote_url:
                        return True
            return False
        except Exception as e:
            print(f"Error checking repository remotes: {e}")
            return False

    @staticmethod
    def upsert_coding_assistant(
        gh_remote_url: str,
        description: Optional[str] = None,
        model: Optional[str] = None,
        show_diffs: Optional[bool] = None,
        dry_run: Optional[bool] = None,
        map_tokens: Optional[int] = None,
        verbose: Optional[bool] = None,
    ) -> str:
        from . import UpsertCodingAssistantModel, MakeService
        coding_assistants, err = CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
            auth=MakeService.auth,
            gh_remote_url=gh_remote_url,
            description=description,
            model=model,
            show_diffs=show_diffs,
            dry_run=dry_run,
            map_tokens=map_tokens,
            verbose=verbose
        )])
        if err is not None:
            return err
        if not CodingAssistantService._is_repo_cloned(coding_assistants[0].repo):
            response = CodingAssistantService.execute_git_command(coding_assistants[0], f"clone {gh_remote_url}")
            if json.loads(response).error:
                return response
            remote_auth_url = CodingAssistantService._construct_github_remote_url(MakeService.auth.gh_user, MakeService.auth.gh_pat, gh_remote_url)
            response = json.loads(CodingAssistantService.execute_git_command(coding_assistants[0], f"remote set-url origin {remote_auth_url}"))
            if json.loads(response).error:
                return response
            return json.dumps({"response": f"Coding assistant(repository: {gh_remote_url}) upserted and repo was cloned locally + authorized using a Personal Access Token."})
        else:
            return json.dumps({"response": f"Coding assistant(repository: {gh_remote_url}) upserted! The repository was already cloned successfully."})

    @staticmethod
    def make_coding_assistant(backend_coding_assistant):
        from . import MakeService
        coding_assistant, err = CodingAssistantService._create_coding_assistant(backend_coding_assistant)
        if err is not None:
            return None, err
        coding_assistant.description = backend_coding_assistant.description
        coding_assistant.model = backend_coding_assistant.model
        coding_assistant.gh_remote_url = backend_coding_assistant.gh_remote_url
        MakeService.CODE_ASSISTANT_REGISTRY[coding_assistant.gh_remote_url] = coding_assistant
        return coding_assistant, None

    @staticmethod
    def upsert_coding_assistants(upsert_models):
        from . import BackendService, GetCodingAssistantModel, MakeService
        # Step 1: Upsert all coding_assistants in batch
        err = BackendService.upsert_backend_coding_assistants(upsert_models)
        if err and err != json.dumps({"error": "No coding_assistants were upserted, no changes found!"}):
            return None, err

        # Step 2: Retrieve all coding assistants from backend in batch
        get_coding_assistant_models = [GetCodingAssistantModel(auth=MakeService.auth, gh_remote_url=model.gh_remote_url) for model in upsert_models]
        backend_coding_assistants, err = BackendService.get_backend_coding_assistants(get_coding_assistant_models)
        if err:
            return None, err
        if len(backend_coding_assistants) == 0:
            return None, json.dumps({"error": "Could not fetch coding_assistants from backend"})

        # Step 3: Update local coding_assistant registry
        successful_coding_assistants = []
        for backend_coding_assistant in backend_coding_assistants:
            coder = MakeService.CODE_ASSISTANT_REGISTRY.get(backend_coding_assistant.gh_remote_url)
            if coder is None:
                coder, err = CodingAssistantService.make_coding_assistant(backend_coding_assistant)
                if err is not None:
                    return None, err
            successful_coding_assistants.append(coder)
        return successful_coding_assistants, None
    
    @staticmethod
    def execute_git_command(coder, git_command):
        try:
            result = coder.repo.git.execute(git_command.split())
            return json.dumps({"response": f"Git command executed successfully: {result}"})
        except coder.repo.git.exc.GitCommandError as e:
            return json.dumps({"error": f"Error executing Git command: {e}"})

    @staticmethod
    def create_github_pull_request(token, repo, title, body, head, base="main"):
        """
        Create a pull request on GitHub.
        
        :param token: Personal access token for the GitHub API
        :param repo: Repository name with owner (e.g., "owner/repo")
        :param title: Title of the pull request
        :param body: Content of the pull request
        :param head: Name of the branch where your changes are implemented
        :param base: Branch you want the changes pulled into (default "main")
        """
        url = f"https://api.github.com/repos/{repo}/pulls"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return json.dumps({"error": f"Pull request created successfully, URL: {response.json()['html_url']}"})
        else:
            return json.dumps({"error": f"Failed to create pull request: {response.content}"})

    @staticmethod
    def _get_repo_name_from_url(remote_url):
        """
        Extract the repository name from a GitHub remote URL.

        :param remote_url: The remote URL of the GitHub repository
        :return: The name of the repository
        """
        # Removing the .git part if present
        if remote_url.endswith('.git'):
            remote_url = remote_url[:-4]

        # Splitting the URL and extracting the repository name
        parts = remote_url.split('/')
        if 'github.com' in remote_url and len(parts) > 1:
            repo_name = parts[-1]  # The repository name is the last part of the URL
            return repo_name
        else:
            raise ValueError("Invalid GitHub URL")

    @staticmethod
    def _create_coding_assistant(backend_coding_assistant):
        from . import MakeService
        coder = None
        try:
            repository_name = CodingAssistantService._get_repo_name_from_url(backend_coding_assistant.gh_remote_url)
            io = InputOutput(pretty=False, yes=True, input_history_file=f".aider.input.history-{repository_name}", chat_history_file=f".aider.chat.history-{repository_name}.md")
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
                git_dname=f"coding\{repository_name}",
                show_diffs=backend_coding_assistant.show_diffs,
                dry_run=backend_coding_assistant.dry_run,
                map_tokens=backend_coding_assistant.map_tokens,
                verbose=backend_coding_assistant.verbose,
            )
        except ValueError as err:
            return None, str(err)
        return coder, None

    @staticmethod
    def send_message_to_coding_assistant(
        gh_remote_url: str,
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
        coder = CodingAssistantService.get_coding_assistant(GetCodingAssistantModel(auth=MakeService.auth, gh_remote_url=gh_remote_url))
        if coder is None:
            return json.dumps({"error": f"Could not send message to coding_assistant: repository ({gh_remote_url}) does not exist."})
        coder.io.console.begin_capture()
        cmd = None
        if command_add:
            coder.commands.cmd_add(command_add)
            cmd = 'add'
            coding_assistants, err = CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
                auth=MakeService.auth,
                gh_remote_url=gh_remote_url,
                files=coder.abs_fnames
            )])
            if err is not None:
                return err
        elif command_drop:
            coder.commands.cmd_drop(command_drop)
            cmd = 'drop'
            coding_assistants, err = CodingAssistantService.upsert_coding_assistants([UpsertCodingAssistantModel(
                auth=MakeService.auth,
                gh_remote_url=gh_remote_url,
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
            repository_name = CodingAssistantService._get_repo_name_from_url(coder.gh_remote_url)
            return CodingAssistantService.create_github_pull_request(MakeService.gh_pat, 
                                                                     repository_name, 
                                                                     pr_title,
                                                                     pr_body,
                                                                     coder.repo.active_branch)
        elif command_git_command:
            return CodingAssistantService.execute_git_command(coder, command_git_command)  
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