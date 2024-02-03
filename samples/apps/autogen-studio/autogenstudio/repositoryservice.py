import requests
import git
import shutil
import logging
import shlex

from typing import Dict
from pathlib import Path
from urllib.parse import urlparse, urlunparse

class RepositoryService:
    @staticmethod
    def _create_github_repository(token: str, name: str, description: str="", private: bool =False):
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
    def _check_repo_exists(username: str, repo_name: str, token: str):
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
    def _fork_repository(token: str, repo_full_name: str):
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
    def _update_github_repository(token: str, username: str, repo_name: str, description: str=None, private: bool=None):
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
    def create_github_remote_repo(auth_dict: Dict, repository_name: str, description: str = None, private: bool = None, gh_remote_url: str = None):
        gh_user = auth_dict["GH_USER"]
        gh_pat = auth_dict["GH_PAT"]
        if not gh_user:
            return {"error": "Github user not set when calling API."}
        if not gh_pat:
            return {"error": "Github personal access token not set when calling API."}
        # Check if the repository already exists under the user's account
        if not RepositoryService._check_repo_exists(gh_user, repository_name, gh_pat):
            # If the repository does not exist, create it
            # check if we need to fork the repository
            if gh_remote_url:
                remote_gh_user = RepositoryService._get_username_from_repo_url(gh_remote_url)
                if 'error' in remote_gh_user:
                    return remote_gh_user
            # if the user's are different it means we are dealing with another remote so we fork
            if gh_remote_url and remote_gh_user != gh_user:
                if not RepositoryService._check_repo_exists(remote_gh_user, repository_name, gh_pat):
                    return {"error": f"Repository({repository_name}) does not exist remotely."}
                # If the repository exists and belongs to a different user, fork it
                gh_remote_url = RepositoryService._fork_repository(gh_pat, f"{remote_gh_user}/{repository_name}")
                if 'error' in gh_remote_url:
                    return gh_remote_url
                if not RepositoryService._check_repo_exists(gh_user, repository_name, gh_pat):
                    return {"error": f"After forking repository({repository_name}) could not locate remote under user {gh_user}."}
            else:
                create_response = RepositoryService._create_github_repository(gh_pat, repository_name, description or "", private or False)
                if 'error' in create_response:
                    return create_response
        else:
            update_response = RepositoryService._update_github_repository(gh_pat, gh_user, repository_name, description, private)
            if 'error' in update_response:
                return update_response
        return f"https://github.com/{gh_user}/{repository_name}.git"

    
    @staticmethod
    def _get_username_from_repo_url(repo_url: str):
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
    def create_github_pull_request(auth_dict: Dict, repository_name: str, title: str, body: str, head_branch: str):
        """
        Create a pull request on GitHub, checking for existing ones first.

        :param repository_name: Name of the repository
        :param title: Title of the pull request
        :param body: Content of the pull request
        :param head_branch: Name of the branch where your changes are implemented
        """
        gh_user = auth_dict["GH_USER"]
        gh_pat = auth_dict["GH_PAT"]
        repo = f"{gh_user}/{repository_name}"
        headers = {"Authorization": f"token {gh_pat}", "Accept": "application/vnd.github.v3+json"}

        # Get repository details to check if it's a fork
        repo_details = requests.get(f"https://api.github.com/repos/{repo}", headers=headers).json()
        parent_repo = repo_details.get('parent', {}).get('full_name', repo)
        head = f"{gh_user}:{head_branch}" if 'parent' in repo_details else head_branch

        # Check for existing pull requests
        prs_url = f"https://api.github.com/repos/{parent_repo}/pulls"
        open_prs = requests.get(prs_url, headers=headers).json()
        for pr in open_prs:
            if pr['head']['label'] == head:
                return {"response": f"Pull request already exists, URL: {pr['html_url']}"}

        # Create the pull request
        pr_data = {"title": title, "body": body, "head": head, "base": "main"}
        response = requests.post(prs_url, headers=headers, json=pr_data)
        if response.status_code == 201:
            return {"response": f"Pull request created successfully, URL: {response.json()['html_url']}"}
        else:
            return {"error": f"Failed to create pull request: {response.json()}"}

    @staticmethod
    def clone_repo(auth_dict: Dict, gh_remote_url: str, workspace: Path):
        gh_user = auth_dict["GH_USER"]
        gh_pat = auth_dict["GH_PAT"]
        # Clone the repository if it's not already cloned
        if RepositoryService._get_username_from_repo_url(gh_remote_url) != gh_user:
            return {"error": f"gh_remote_url ({gh_remote_url}) belongs to another user, not the one you used: {gh_user}"}
        if workspace.is_dir() and not any(workspace.iterdir()):
            shutil.rmtree(workspace)
        elif workspace.is_file():
            workspace.unlink()
        if not workspace.exists():
            repo, clone_response = RepositoryService._clone_repository(gh_remote_url, workspace)
            if 'error' in clone_response:
                if workspace.is_dir():
                    shutil.rmtree(workspace)
                return clone_response
            is_cloned = RepositoryService._is_repo_cloned(repo, gh_remote_url)
            if not is_cloned:
                if workspace.is_dir():
                    shutil.rmtree(workspace)
                return RepositoryService.clone_repo(auth_dict, gh_remote_url, workspace)
            # Set remote URL with PAT for authentication
            remote_auth_url = RepositoryService._construct_github_remote_url_with_pat(gh_user, gh_pat, gh_remote_url)
            if 'error' in remote_auth_url:
                if workspace.is_dir():
                    shutil.rmtree(workspace)
                return RepositoryService.clone_repo(auth_dict, gh_remote_url, workspace)
            # set the auth so you can push
            set_remote_response = RepositoryService.execute_git_command(repo, f"remote set-url origin {remote_auth_url}")
            if 'error' in set_remote_response:
                if workspace.is_dir():
                    shutil.rmtree(workspace)
                return RepositoryService.clone_repo(auth_dict, gh_remote_url, workspace)
             # setup docs
            setup_docs_response = RepositoryService.setup_doc_dirs(repo, workspace)
            if 'error' in setup_docs_response:
                if workspace.is_dir():
                    shutil.rmtree(workspace)
                return RepositoryService.clone_repo(auth_dict, gh_remote_url, workspace)
                       
            return {"response": f"Repository was successfully cloned + authorized using a Personal Access Token to remote: {gh_remote_url}."}
        else:
            try:
                repo = git.Repo(workspace, search_parent_directories=False)
            except Exception as e:
                if workspace.is_dir():
                    shutil.rmtree(workspace)
                return RepositoryService.clone_repo(auth_dict, gh_remote_url, workspace)
            if not repo.remotes:
                if workspace.is_dir():
                    shutil.rmtree(workspace)
                return RepositoryService.clone_repo(auth_dict, gh_remote_url, workspace)
            is_cloned = RepositoryService._is_repo_cloned(repo, gh_remote_url)
            if not is_cloned:
                if workspace.is_dir():
                    shutil.rmtree(workspace)
                return RepositoryService.clone_repo(auth_dict, gh_remote_url, workspace)
            return {"response": "The repository was already cloned."}

    @staticmethod
    def _clone_repository(repo_url: str, workspace: Path):
        try:
            repo = git.Repo.clone_from(repo_url, workspace)
            gitignore_filename = workspace / ".gitignore"
            if not gitignore_filename.exists():
                ignores = ["__pycache__", ".*", ".git/", ".aider*/", "*.pyc"]
                with open(str(gitignore_filename), mode="w") as writer:
                    writer.write("\n".join(ignores))
                repo.index.add([".gitignore"])
                repo.index.commit("Add .gitignore")
            return repo, {"response": f"Repository cloned successfully to {workspace}"}
        except Exception as e:
            logging.error(f"Error during cloning: {e}")
            return None, {"error": f"Error cloning repository: {e}"}
            
    @staticmethod
    def _remove_auth_from_url(url: str) -> str:
        """
        Remove the authentication part from the URL.

        :param url: URL to process
        :return: URL without the authentication part
        """
        parsed_url = urlparse(url)
        # Reconstruct the URL without the username and password
        return urlunparse((parsed_url.scheme, parsed_url.hostname, parsed_url.path, '', '', ''))

    @staticmethod
    def _is_repo_cloned(repo: git.Repo, remote_url: str) -> bool:
        """
        Check if the GitPython Repo object is associated with the given remote URL.

        :param repo: GitPython Repo object
        :param remote_url: URL of the remote repository to check
        :return: True if the Repo is cloned from the remote URL, False otherwise
        """
        if not remote_url or not repo:
            return False

        try:
            for remote in repo.remotes:
                for url in remote.urls:
                    clean_url = RepositoryService._remove_auth_from_url(url)
                    if clean_url == remote_url:
                        return True
            return False
        except Exception as e:
            return False

    @staticmethod
    def _construct_github_remote_url_with_pat(gh_user: str, gh_pat: str, gh_remote_url: str):
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
    
    @staticmethod
    def execute_git_command(repo: git.Repo, git_command: str):
        try:
            # Use shlex.split to correctly handle spaces within quotes
            command_parts = shlex.split(git_command)

            # Prepend "git" if it's not the first part of the command
            if command_parts[0] != 'git':
                command_parts.insert(0, 'git')

            # Execute the git command
            result = repo.git.execute(command_parts)
            return {"response": f"Git command executed successfully: {result}"}
        except Exception as e:
            return {"error": f"Error executing Git command: {e}"}
    
    @staticmethod
    def setup_doc_dirs(repo: git.Repo, workspace: Path):
        doc_files = {
            "docs/product_management/goals.txt": "Product Goals: Outline up to three key goals for the product.\n",
            "docs/product_management/user_stories.txt": "User Stories: Describe 3-5 scenarios highlighting user interactions with the product.\n",
            "docs/product_management/competition.txt": "Competitive Analysis: List 5-7 competitors and analyze their offerings.\n",
            "docs/product_management/requirements.txt": "Requirements: Detail the top 5 requirements with priorities (P0, P1, P2).\n",
            "docs/product_management/ui_design.txt": "UI Design Draft: Describe UI elements, functions, style, and layout.\n",
            "docs/product_management/anything_unclear.txt": "Anything UNCLEAR: Highlight unclear aspects of the project and seek clarifications.\n",
            "docs/architect/implementation.txt": "Implementation Approach: Discuss difficult points and select appropriate frameworks.\n",
            "docs/architect/structure.txt": "Data Structures and Interfaces: Provide detailed data structures and comprehensive API designs.\n",
            "docs/architect/program_flow.txt": "Program Call Flow: Describe the call flow using the classes and APIs defined.\n",
            "docs/architect/anything_unclear.txt": "Anything UNCLEAR: Address unclear aspects in the architecture and seek clarifications.\n",
            "docs/project_management/requirements.txt": "Required Python Packages: List Python packages needed, formatted as in requirements.txt.\n",
            "docs/project_management/third_party_packages.txt": "Required Other Language Packages: List packages for languages other than Python.\n",
            "docs/project_management/logic_analysis.txt": "Logic Analysis: List files with classes/methods/functions and their dependencies.\n",
            "docs/project_management/tasks.txt": "Task List: Break down tasks into filenames, prioritized by dependency order.\n",
            "docs/project_management/api_spec.txt": "Full API Spec: Describe all APIs using OpenAPI 3.0 spec for front and back-end communication.\n",
            "docs/project_management/shared_knowledge.txt": "Shared Knowledge: Detail shared utility functions or configuration variables.\n",
            "docs/project_management/anything_unclear.txt": "Anything UNCLEAR: Highlight unclear aspects in project management and seek clarifications.\n"
        }

        try:
            for filepath, content in doc_files.items():
                full_path = workspace / filepath
                full_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
                with open(full_path, "w") as file:
                    file.write(content)
                repo.index.add([str(full_path)])
            repo.index.commit("Add documentation structure and files with descriptions")
            return {"response": "Documentation directories and files setup and committed with descriptions"}
        except Exception as e:
            return {"error": f"Error setting up documentation directories: {e}"}
