
from typing import Optional
from openai import OpenAI
import json
import requests
class CodeRepositoryService:
    @staticmethod
    def get_code_repository(coding_repository_model):
        from . import BackendService, MakeService, BaseCodeRepository, DeleteCodeRepositoryModel
        code_repository: BaseCodeRepository = MakeService.CODE_REPOSITORY_REGISTRY.get(coding_repository_model.name)
        if code_repository is None:
            backend_code_repositories, err = BackendService.get_backend_code_repository([coding_repository_model])
            if err is None and backend_code_repositories:
                code_repository, err = CodeRepositoryService.make_code_repository(backend_code_repositories[0])
                if err is None and code_repository:
                    MakeService.CODE_REPOSITORY_REGISTRY[coding_repository_model.name] = code_repository
                else:
                    BackendService.delete_backend_code_repositories([DeleteCodeRepositoryModel(auth=coding_repository_model.auth, name=coding_repository_model.name)])
        return code_repository
    
    @staticmethod
    def get_code_repository_info(name: str) -> str:
        from . import MakeService, CodeRepositoryInfo, GetCodeRepositoryModel
        backend_code_repository = CodeRepositoryService.get_code_repository(GetCodeRepositoryModel(auth=MakeService.auth, name=name))
        if not backend_code_repository:
            return json.dumps({"error": f"Code repository({name}) not found"})
        is_forked = CodeRepositoryService._is_github_repo_a_fork(backend_code_repository.gh_remote_url, MakeService.auth.gh_pat)
        repo_description = MakeService._get_short_description(backend_code_repository.description)
        backend_code_repository_info = CodeRepositoryInfo(
            name=name,
            upstream_gh_remote_url=backend_code_repository.upstream_gh_remote_url,
            gh_remote_url=backend_code_repository.gh_remote_url,
            private=backend_code_repository.private,
            description=repo_description,
            is_forked=is_forked,
            associated_code_assistants=backend_code_repository.associated_code_assistants
        )
        return json.dumps({"response": backend_code_repository_info.dict()})

    @staticmethod
    def discover_code_repositories(query: str) -> str:
        from . import BackendService, DiscoverCodeRepositoryModel, MakeService
        response, err = BackendService.discover_backend_code_repositories(DiscoverCodeRepositoryModel(auth=MakeService.auth, query=query))
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
            return {"response": f"Repository ({name}) created successfully!"}
        elif response.status_code == 422:
            return {"response": f"Repository ({name}) already exists!"}
        else:
            return {"error": f"Failed to create repository: {response.json()}"}
    
    @staticmethod
    def _check_repo_exists(username, repo_name, token):
        """
        Check if a repository exists on GitHub.

        :param username: GitHub username
        :param repo_name: Repository name
        :param token: GitHub Personal Access Token
        :return: True if repository exists, False otherwise
        """
        url = f"https://api.github.com/repos/{username}/{repo_name}"
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers)
        return response.status_code == 200

    @staticmethod
    def _fork_repository(token, repo_full_name):
        """
        Fork a repository on GitHub.

        :param token: GitHub Personal Access Token
        :param repo_full_name: Full name of the repository (e.g., "original-owner/repo")
        :return: URL of the forked repository, or error message
        """
        url = f"https://api.github.com/repos/{repo_full_name}/forks"
        headers = {"Authorization": f"token {token}"}
        response = requests.post(url, headers=headers)
        if response.status_code == 202:  # 202 Accepted indicates forking initiated
            return response.json()['html_url']
        else:
            return {"error": f"Failed to fork repository: {response.json().get('message', 'Unknown error')}"}


    @staticmethod
    def _update_github_repository(token, username, repo_name, description=None, private=None):
        """
        Update an existing GitHub repository's description or privacy setting.

        :param token: Personal access token for the GitHub API
        :param username: GitHub username
        :param repo_name: Name of the repository
        :param description: New description for the repository
        :param private: Boolean indicating whether the repository should be private
        :return: A response indicating success or failure
        """
        url = f"https://api.github.com/repos/{username}/{repo_name}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Constructing the data payload
        data = {}
        if description is not None:
            data['description'] = description
        if private is not None:
            data['private'] = private

        # Only send a request if there's something to update
        if data:
            response = requests.patch(url, headers=headers, json=data)
            if response.status_code in [200, 202]:  # 200 OK or 202 Accepted
                return {"response": f"Repository '{repo_name}' updated successfully!"}
            else:
                return {"error": f"Failed to update repository: {response.json()}"}
        else:
            return {"response": "No updates to perform."}


    @staticmethod
    def create_github_remote_repo(repository_name: str, description:str = None, private: bool = None, gh_remote_url: str = None):
        from . import MakeService

        gh_user = MakeService.auth.gh_user
        gh_pat = MakeService.auth.gh_pat
        if not gh_user:
            return json.dumps({"error": "Github user not set when calling API."})
        if not gh_pat:
            return json.dumps({"error": "Github personal access token not set when calling API."})
        # Check if the repository already exists under the user's account
        if not CodeRepositoryService._check_repo_exists(gh_user, repository_name, gh_pat):
            # If the repository does not exist, create it
            # check if we need to fork the repository
            if gh_remote_url:
                remote_gh_user = CodeRepositoryService._get_username_from_repo_url(gh_remote_url)
                if isinstance(remote_gh_user, dict) and 'error' in remote_gh_user:
                    return json.dumps(remote_gh_user)
            # if the user's are different it means we are dealing with another remote so we fork
            if gh_remote_url and remote_gh_user != gh_user:
                if not CodeRepositoryService._check_repo_exists(remote_gh_user, repository_name, gh_pat):
                    return json.dumps({"error": f"Repository({repository_name}) does not exist remotely."})
                # If the repository exists and belongs to a different user, fork it
                gh_remote_url = CodeRepositoryService._fork_repository(gh_pat, f"{remote_gh_user}/{repository_name}")
                if isinstance(gh_remote_url, dict) and 'error' in gh_remote_url:
                    return json.dumps(gh_remote_url)
                if not CodeRepositoryService._check_repo_exists(gh_user, repository_name, gh_pat):
                    return json.dumps({"error": f"After forking repository({repository_name}) could not locate remote under user {gh_user}."})
            else:
                create_response = CodeRepositoryService._create_github_repository(gh_pat, repository_name, description or "", private or False)
                if isinstance(create_response, dict) and 'error' in create_response:
                    return json.dumps(create_response)
        else:
            CodeRepositoryService._update_github_repository(gh_pat, gh_user, repository_name, description, private)
            if isinstance(create_response, dict) and 'error' in create_response:
                return json.dumps(create_response)
        return json.dumps({"response": f"https://github.com/{gh_user}/{repository_name}.git"})

    @staticmethod
    def clone_repo(coder, cr):
        from . import MakeService, CodingAssistantService
        # Clone the repository if it's not already cloned
        is_cloned = CodeRepositoryService._is_repo_cloned(coder.repo, cr.gh_remote_url)
        if not is_cloned:
            clone_response = CodeRepositoryService._clone_repository(coder, cr.gh_remote_url, "coding")
            if isinstance(clone_response, dict) and 'error' in clone_response:
                return clone_response
            is_cloned = CodeRepositoryService._is_repo_cloned(coder.repo, cr.gh_remote_url)
            if isinstance(is_cloned, dict) and 'error' in is_cloned:
                return is_cloned
            if not is_cloned:
                return {"error": f"Repository({cr.gh_remote_url}) was not cloned."}
            # Set remote URL with PAT for authentication
            remote_auth_url = CodeRepositoryService._construct_github_remote_url_with_pat(MakeService.auth.gh_user, MakeService.auth.gh_pat, cr.gh_remote_url)
            if isinstance(remote_auth_url, dict) and 'error' in remote_auth_url:
                return json.dumps(remote_auth_url)
            set_remote_response = json.loads(CodingAssistantService._execute_git_command(coder, f"remote set-url origin {remote_auth_url}"))
            if isinstance(set_remote_response, dict) and 'error' in set_remote_response:
                return json.dumps(set_remote_response)
            return {"response": f"Repository was successfully cloned + authorized using a Personal Access Token to remote: {cr.gh_remote_url}."}
        else:
            return {"response": "The repository was already cloned."}

    @staticmethod
    def _construct_github_remote_url_with_pat(gh_user, gh_pat, gh_remote_url):
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
            return {"error": "Invalid GitHub remote URL"}

        # Construct the new URL with username and PAT
        new_url = f"https://{gh_user}:{gh_pat}@{url_parts[1]}"
        return new_url

    def _clone_repository(coder, repo_url, local_path):
        try:
            coder.repo.git.Repo.clone_from(repo_url, local_path)
            return {"response": f"Repository cloned successfully to {local_path}"}
        except coder.repo.git.exc.GitCommandError as e:
            return {"error": f"Error cloning repository: {e}"}
            
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
            return {"error": f"Error checking repository remotes: {e}"}

    @staticmethod
    def upsert_code_repository(
        name: str,
        description: Optional[str] = None,
        private: Optional[bool] = None,
        gh_remote_url: Optional[str] = None,
    ) -> str:
        from . import UpsertCodeRepositoryModel, MakeService
        
        working_gh_remote_url_response = CodeRepositoryService.create_github_remote_repo(name, description, private, gh_remote_url)
        if isinstance(working_gh_remote_url_response, dict) and 'error' in working_gh_remote_url_response:
            return json.dumps(working_gh_remote_url_response)
        working_gh_remote_url = working_gh_remote_url_response['response']
        code_repositories, err = CodeRepositoryService.upsert_code_repositories([UpsertCodeRepositoryModel(
            auth=MakeService.auth,
            name=name,
            description=description,
            private=private,
            upstream_gh_remote_url=gh_remote_url,
            gh_remote_url=working_gh_remote_url
        )])
        if err is not None:
            return err
        return json.dumps({"response": f"Coding repository({name}) upserted!"})

    @staticmethod
    def make_code_repository(backend_code_repository):
        from . import MakeService, BaseCodeRepository
        code_repository = BaseCodeRepository()
        code_repository.name = backend_code_repository.name
        code_repository.description = backend_code_repository.description
        code_repository.private = backend_code_repository.private
        code_repository.gh_remote_url = backend_code_repository.gh_remote_url
        code_repository.upstream_gh_remote_url = backend_code_repository.upstream_gh_remote_url
        code_repository.associated_code_assistants = backend_code_repository.associated_code_assistants
        MakeService.CODE_REPOSITORY_REGISTRY[code_repository.name] = code_repository
        return code_repository, None

    @staticmethod
    def upsert_code_repositories(upsert_models):
        from . import BackendService, GetCodeRepositoryModel, MakeService, DeleteCodeRepositoryModel
        # Step 1: Upsert all in batch
        err = BackendService.upsert_backend_code_repositories(upsert_models)
        if err and err != json.dumps({"error": "No repositories were upserted, no changes found!"}):
            return None, err

        # Step 2: Retrieve all from backend in batch
        get_code_repository_models = [GetCodeRepositoryModel(auth=MakeService.auth, name=model.name) for model in upsert_models]
        backend_code_repositories, err = BackendService.get_backend_code_repositories(get_code_repository_models)
        if err:
            return None, err
        if len(backend_code_repositories) == 0:
            return None, json.dumps({"error": "Could not fetch code_repositories from backend"})

        # Step 3: Update local code_repository registry
        successful_code_repositories = []
        for backend_code_repository in backend_code_repositories:
            coder, err = CodeRepositoryService.make_code_repository(backend_code_repository)
            if err is not None:
                BackendService.delete_backend_code_repositories([DeleteCodeRepositoryModel(auth=backend_code_repository.auth, name=backend_code_repository.name)])
                return None, err
            successful_code_repositories.append(coder)
        return successful_code_repositories, None
    
    @staticmethod
    def _get_username_from_repo_url(repo_url):
        """
        Extract the username from a GitHub repository URL.

        :param repo_url: The full URL of the GitHub repository
        :return: Username of the repository owner
        """
        # Check for common Git URL formats: HTTPS and SSH
        if repo_url.startswith("https://"):
            # HTTPS URL format: https://github.com/username/repo_name
            parts = repo_url.split('/')
            if 'github.com' in parts and len(parts) > 3:
                return parts[3]  # Username is the fourth element
        elif repo_url.startswith("git@"):
            # SSH URL format: git@github.com:username/repo_name.git
            parts = repo_url.split(':')
            if len(parts) == 2:
                subparts = parts[1].split('/')
                if len(subparts) > 1:
                    return subparts[0]  # Username is before the repo name
        else:
            return {"error": "Invalid or unsupported Git URL format"}

        return {"error": "Username could not be extracted from the URL"}
    
    @staticmethod
    def _is_github_repo_a_fork(repo_url, token):
        """
        Check if a GitHub repository is a fork using its URL.

        :param repo_url: The full URL of the GitHub repository
        :param token: GitHub Personal Access Token
        :return: True if the repository is a fork, False otherwise
        """
        # Extracting username and repository name from the URL
        if repo_url.startswith("https://"):
            parts = repo_url.split('/')
            if 'github.com' in parts and len(parts) > 4:
                username = parts[3]
                repo_name = parts[4].replace('.git', '')  # Remove .git if present
        elif repo_url.startswith("git@"):
            parts = repo_url.split(':')
            if len(parts) == 2:
                subparts = parts[1].split('/')
                if len(subparts) > 1:
                    username = subparts[0]  # Username is before the repo name
                    repo_name = subparts[1].replace('.git', '')  # Remove .git if present
        else:
            return {"error": "Invalid or unsupported GitHub URL format"}

        # GitHub API URL to check repository details
        api_url = f"https://api.github.com/repos/{username}/{repo_name}"
        headers = {"Authorization": f"token {token}"}

        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            repo_data = response.json()
            return repo_data.get('fork', False)
        else:
            return {"error": f"Failed to get repository details: {response.status_code}"}
        