
from typing import Optional
from aider import models
from aider.coders import Coder
from aider.io import InputOutput
from openai import OpenAI
from typing import Set
import json
import logging
from .repositoryservice import RepositoryService
import os
from pathlib import Path

class CodingAssistantService:
    assistants_exist: Set[str] = {}
    
    @staticmethod
    def create_coding_assistant(
        assistant_name: str,
        description: Optional[str] = None,
        gh_remote_url: Optional[str] = None,
        private: Optional[bool] = None,
    ) -> str:
        if not assistant_name:
            return None, {"error": "assistant_name not provided!"}
        auth_dict = {
            "GH_USER": os.environ.get("GH_USER"),
            "GH_PAT": os.environ.get("GH_PAT"),
        }
        # Get the directory of the current script
        script_dir = Path(os.getcwd())
        user_workspace = script_dir / assistant_name
        print(f'user_workspace {user_workspace}')
        user_workspace.mkdir(parents=True, exist_ok=True)
        if assistant_name not in CodingAssistantService.assistants_exist:
            working_gh_remote_url_response = RepositoryService.create_github_remote_repo(auth_dict, assistant_name, description, private, gh_remote_url)
            if 'error' in working_gh_remote_url_response:
                return None, working_gh_remote_url_response
            clone_response = RepositoryService.clone_repo(auth_dict, working_gh_remote_url_response, user_workspace)
            if 'error' in clone_response:
                return None, clone_response
        
        io = InputOutput(pretty=True, yes=True, input_history_file=f".aider.input.history-{assistant_name}", chat_history_file=f".aider.chat.history-{assistant_name}.md")
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        main_model = models.Model.create("gpt-4-turbo-preview", client)
        coder = Coder.create(
            main_model=main_model,
            edit_format=None,
            io=io,
            skip_model_availabily_check=False,
            client=client,
            ##
            git_dname=user_workspace,
        )
        if assistant_name not in CodingAssistantService.assistants_exist:
            coder.commands.cmd_add("docs/**/*")
            CodingAssistantService.assistants_exist.add(assistant_name)
        return coder, None
        
    @staticmethod
    def run_code_assistant(
        coder: Coder,
        command_message: str):
        try:
            coder.io.add_to_input_history(command_message)
            coder.io.tool_output()
            coder.run(with_message=command_message)
        except Exception as e:
            return json.dumps({"error": f"Exception from running assistant: {str(e)}"})

    @staticmethod
    def read_text(file_path: str) -> tuple[str, Optional[str]]:
        try:
            with open(file_path, 'r') as file:
                text = file.read()
            return text, None
        except Exception as e:
            return None, json.dumps({"error": str(e)})

    @staticmethod
    def show_file(command_show_file: str):
        # Read and return the file content if it is within the workspace
        text, err = CodingAssistantService.read_text(command_show_file)
        if err is not None:
            return None, err
        return text, None
        
    @staticmethod
    def send_command_to_coding_assistant(
        assistant_name: str,
        command: str,
        args: Optional[str] = None,
        gh_remote_url: Optional[str] = None,
        description: Optional[str] = None,
        private: Optional[bool] = None
    ) -> str:
        coder, err = CodingAssistantService.create_coding_assistant(assistant_name, description, gh_remote_url, private)
        if err:
            return err
        if command == "cmd_message":
            if not args:
                return json.dumps({"error": "No message provided to coding assistant in the args parameter!"})
            return CodingAssistantService.run_code_assistant(coder, args)
        elif command == "cmd_clear":
            logging.info("manage_coding_assistant cmd_clear")
            coder.commands.cmd_clear(None)
        elif command == "cmd_ls":
            logging.info("manage_coding_assistant cmd_ls")
            coder.commands.cmd_ls(None)
        elif command == "cmd_undo":
            logging.info("manage_coding_assistant cmd_undo")
            coder.commands.cmd_undo(None)
        elif command == "cmd_diff":
            logging.info("manage_coding_assistant cmd_diff")
            coder.commands.cmd_diff(None)
        elif command == "cmd_git":
            logging.info("manage_coding_assistant cmd_git")
            coder.commands.cmd_git(args)
        elif command == "cmd_test":
            logging.info("manage_coding_assistant cmd_test")
            coder.commands.cmd_test(args)
        elif command == "cmd_run":
            logging.info("manage_coding_assistant cmd_run")
            coder.commands.cmd_run(args)
        elif command == "cmd_diff":
            logging.info("manage_coding_assistant cmd_diff")
            coder.commands.cmd_diff(None)
        elif command == "cmd_tokens":
            logging.info("manage_coding_assistant cmd_tokens")
            coder.commands.cmd_tokens(None)
        elif command == "get_repo_map":
            logging.info("manage_coding_assistant get_repo_map")
            repo_map = coder.get_repo_map()
            if repo_map:
                coder.io.tool_output(repo_map)
        elif command == "cmd_pr":
            return RepositoryService.create_github_pull_request(
                repository_name=assistant_name,
                title=f"PR push from autogen agent {assistant_name}",
                body=args,
                branch=coder.repo.active_branch
            )
        elif command == "show_file":
            logging.info(f"manage_coding_assistant command_show_file {command}")
            text, err = CodingAssistantService.show_file(args)
            if err is not None:
                logging.error(f"command_show_file failed: {err}")
                return err
            return text
        else:
            return json.dumps({"error": "Could not manage code assistant, no commands or message provided"})

        return json.dumps({"success": f"{command} finished"})