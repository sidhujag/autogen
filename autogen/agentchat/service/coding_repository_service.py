
from typing import Optional
import json

class CodeRepositoryService:
    @staticmethod
    def get_code_repository(coding_repository_model):
        from . import BackendService, MakeService, BaseCodeRepository, DeleteCodeRepositoryModel
        code_repository: BaseCodeRepository = MakeService.CODE_REPOSITORY_REGISTRY.get(coding_repository_model.name)
        if code_repository is None:
            backend_code_repositories, err = BackendService.get_backend_code_repositories([coding_repository_model])
            if err is None and backend_code_repositories:
                code_repository, err = CodeRepositoryService.make_code_repository(backend_code_repositories[0])
                if err is None and code_repository:
                    MakeService.CODE_REPOSITORY_REGISTRY[coding_repository_model.name] = code_repository
                else:
                    BackendService.delete_backend_code_repositories([DeleteCodeRepositoryModel(name=coding_repository_model.name)])
        return code_repository
    
    @staticmethod
    def get_code_repository_info(repository_name: str) -> str:
        from . import MakeService, CodeRepositoryInfo, GetCodeRepositoryModel
        backend_code_repository = CodeRepositoryService.get_code_repository(GetCodeRepositoryModel(name=repository_name))
        if not backend_code_repository:
            return json.dumps({"error": f"Code repository({repository_name}) not found"})
        repo_description = MakeService._get_short_description(backend_code_repository.description)
        backend_code_repository_info = CodeRepositoryInfo(
            name=repository_name,
            gh_remote_url=backend_code_repository.gh_remote_url,
            private=backend_code_repository.private,
            description=repo_description,
            is_forked=backend_code_repository.is_forked,
            associated_code_assistants=backend_code_repository.associated_code_assistants,
        )
        return json.dumps({"response": backend_code_repository_info.dict()})

    @staticmethod
    def discover_code_repositories(query: str) -> str:
        from . import BackendService, DiscoverCodeRepositoryModel
        response, err = BackendService.discover_backend_code_repositories(DiscoverCodeRepositoryModel(query=query))
        if err is not None:
            return err
        return response

    @staticmethod
    def upsert_code_repository(
        repository_name: Optional[str] = None,
        repo_name: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        private: Optional[bool] = None,
        gh_remote_url: Optional[str] = None,
    ) -> str:
        from . import UpsertCodeRepositoryModel
        rep_name = repository_name or repo_name or name
        if not rep_name:
            return json.dumps({"error": "repository_name not provided!"})
        code_repositories, err = CodeRepositoryService.upsert_code_repositories([UpsertCodeRepositoryModel(
            name=rep_name,
            description=description,
            private=private,
            gh_remote_url=gh_remote_url
        )])
        if err is not None:
            return err
        return json.dumps({"response": f"Coding repository({repository_name}) upserted!"})

    @staticmethod
    def make_code_repository(backend_code_repository):
        from . import MakeService, BaseCodeRepository
        code_repository = BaseCodeRepository()
        code_repository.name = backend_code_repository.name
        code_repository.description = backend_code_repository.description
        code_repository.private = backend_code_repository.private
        code_repository.gh_remote_url = backend_code_repository.gh_remote_url
        code_repository.workspace = backend_code_repository.workspace
        code_repository.is_forked = backend_code_repository.is_forked
        code_repository.associated_code_assistants = backend_code_repository.associated_code_assistants
        MakeService.CODE_REPOSITORY_REGISTRY[code_repository.name] = code_repository
        return code_repository, None

    @staticmethod
    def upsert_code_repositories(upsert_models):
        from . import BackendService, GetCodeRepositoryModel, DeleteCodeRepositoryModel
        # Step 1: Upsert all in batch
        err = BackendService.upsert_backend_code_repositories(upsert_models)
        if err and err != json.dumps({"error": "No code repositories were upserted, no changes found!"}):
            return None, err

        # Step 2: Retrieve all from backend in batch
        get_code_repository_models = [GetCodeRepositoryModel(name=model.name) for model in upsert_models]
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
                BackendService.delete_backend_code_repositories([DeleteCodeRepositoryModel(name=backend_code_repository.name)])
                return None, err
            successful_code_repositories.append(coder)
        return successful_code_repositories, None