import json
import os
import traceback
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from openai import OpenAIError
from ..version import VERSION
from ..datamodel import (
    ChatWebRequestModel,
    DBWebRequestModel,
    DeleteMessageWebRequestModel,
    Message,
    Session,
    UpsertWorkflowSession
)
from ..utils import md5_hash, init_webserver_folders, DBManager, dbutils, test_model

from ..chatmanager import AutoGenChatManager


app = FastAPI()


# allow cross origin requests for testing on localhost:800* ports only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://localhost:8080",
        "http://localhost:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


root_file_path = os.environ.get("AUTOGENSTUDIO_APPDIR") or os.path.dirname(os.path.abspath(__file__))
# init folders skills, workdir, static, files etc
folders = init_webserver_folders(root_file_path)
ui_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")

api = FastAPI(root_path="/api")
# mount an api route such that the main route serves the ui and the /api
app.mount("/api", api)

app.mount("/", StaticFiles(directory=ui_folder_path, html=True), name="ui")
api.mount("/files", StaticFiles(directory=folders["files_static_root"], html=True), name="files")


db_path = os.path.join(root_file_path, "database.sqlite")
dbmanager = DBManager(path=db_path)  # manage database operations
chatmanager = AutoGenChatManager()  # manage calls to autogen


@api.post("/messages")
async def add_message(req: ChatWebRequestModel):
    message = Message(**req.message.dict())

    # save incoming message to db
    dbutils.create_message(message=message, dbmanager=dbmanager)
    user_dir = os.path.join(folders["files_static_root"], "user", md5_hash(message.user_id))
    os.makedirs(user_dir, exist_ok=True)

    try:
        response_message: Message = chatmanager.chat(
            message=message,
            work_dir=user_dir,
            flow_config=req.flow_config,
        )

        # save assistant response to db
        dbutils.create_message(message=response_message, dbmanager=dbmanager)
        response = {
            "status": True,
            "message": response_message.content,
            "metadata": json.loads(response_message.metadata),
        }
        return response
    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while processing message: " + str(ex_error),
        }


@api.get("/messages")
async def get_messages(user_id: str = None, session_id: str = None):
    if user_id is None:
        raise HTTPException(status_code=400, detail="user_id is required")
    try:
        user_history = dbutils.get_messages(user_id=user_id, session_id=session_id, dbmanager=dbmanager)

        return {
            "status": True,
            "data": user_history,
            "message": "Messages retrieved successfully",
        }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving messages: " + str(ex_error),
        }


@api.get("/gallery")
async def get_gallery_items(gallery_id: str = None):
    try:
        gallery = dbutils.get_gallery(gallery_id=gallery_id, dbmanager=dbmanager)
        return {
            "status": True,
            "data": gallery,
            "message": "Gallery items retrieved successfully",
        }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving messages: " + str(ex_error),
        }

@api.get("/session")
async def get_session(id: str):
    try:
        session = dbutils.get_session(id, dbmanager=dbmanager)
        if session:
            return {
                "status": True,
                "message": "Session retrieved successfully",
                "data": session,
            }
        else:
            return {
                "status": False,
                "message": "Session not found"
            }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving session: " + str(ex_error),
        }

@api.get("/sessions")
async def get_user_sessions(user_id: str = None):
    """Return a list of all sessions for a user"""
    if user_id is None:
        raise HTTPException(status_code=400, detail="user_id is required")

    try:
        user_sessions = dbutils.get_sessions(user_id=user_id, dbmanager=dbmanager)

        return {
            "status": True,
            "data": user_sessions,
            "message": "Sessions retrieved successfully",
        }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving sessions: " + str(ex_error),
        }


@api.post("/sessions")
async def create_user_session(req: DBWebRequestModel):
    """Create a new session for a user"""
    # print(req.session, "**********" )

    try:
        session = Session(id=req.session.id, user_id=req.session.user_id, flow_config=req.session.flow_config)
        user_sessions = dbutils.create_session(user_id=req.user_id, session=session, dbmanager=dbmanager)
        return {
            "status": True,
            "message": "Session created successfully",
            "data": user_sessions,
        }
    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while creating session: " + str(ex_error),
        }


@api.post("/sessions/publish")
async def publish_user_session_to_gallery(req: DBWebRequestModel):
    """Create a new session for a user"""

    try:
        gallery_item = dbutils.create_gallery(req.session, tags=req.tags, dbmanager=dbmanager)
        return {
            "status": True,
            "message": "Session successfully published",
            "data": gallery_item,
        }
    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred  while publishing session: " + str(ex_error),
        }


@api.delete("/sessions/delete")
async def delete_user_session(req: DBWebRequestModel):
    """Delete a session for a user"""

    try:
        sessions = dbutils.delete_session(session=req.session, dbmanager=dbmanager)
        return {
            "status": True,
            "message": "Session deleted successfully",
            "data": sessions,
        }
    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while deleting session: " + str(ex_error),
        }


@api.post("/messages/delete")
async def remove_message(req: DeleteMessageWebRequestModel):
    """Delete a message from the database"""

    try:
        messages = dbutils.delete_message(
            user_id=req.user_id, msg_id=req.msg_id, session_id=req.session_id, dbmanager=dbmanager
        )
        return {
            "status": True,
            "message": "Message deleted successfully",
            "data": messages,
        }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while deleting message: " + str(ex_error),
        }


@api.get("/skills")
async def get_user_skills(user_id: str):
    try:
        skills = dbutils.get_skills(user_id, dbmanager=dbmanager)

        return {
            "status": True,
            "message": "Skills retrieved successfully",
            "data": skills,
        }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving skills: " + str(ex_error),
        }

@api.post("/discover_services")
async def discover_services(req: DBWebRequestModel):
    try:
        services = dbutils.discover_services(req.msg_id, req.user_id, req.tags, dbmanager=dbmanager)
        if services:
            return {
                "status": True,
                "message": "Services discovered successfully",
                "data": services,
            }
        else:
            return {
                "status": False,
                "message": "Invalid service type",
            }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while discovering services: " + str(ex_error),
        }
        
@api.get("/skill")
async def get_skill(id: str):
    try:
        skill = dbutils.get_skill(id, dbmanager=dbmanager)
        if skill:
            return {
                "status": True,
                "message": "Skill retrieved successfully",
                "data": skill,
            }
        else:
            return {
                "status": False,
                "message": "Skill not found"
            }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving skill: " + str(ex_error),
        }


@api.post("/skills")
async def create_user_skills(req: DBWebRequestModel):
    try:
        skills = dbutils.upsert_skill(skill=req.skill, dbmanager=dbmanager)
        return {
            "status": True,
            "message": "Skill upserted successfully",
            "data": skills,
        }

    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while upserting skills: " + str(ex_error),
        }


@api.delete("/skills/delete")
async def delete_user_skills(req: DBWebRequestModel):
    """Delete a skill for a user"""

    try:
        skills = dbutils.delete_skill(req.skill, dbmanager=dbmanager)

        return {
            "status": True,
            "message": "Skill deleted successfully",
            "data": skills,
        }

    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while deleting skill: " + str(ex_error),
        }

@api.get("/agents")
async def get_user_agents(user_id: str):
    try:
        agents = dbutils.get_agents(user_id, dbmanager=dbmanager)

        return {
            "status": True,
            "message": "Agents retrieved successfully",
            "data": agents,
        }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving agents: " + str(ex_error),
        }

@api.get("/agent")
async def get_agent(id: str):
    try:
        agent = dbutils.get_agent(id, dbmanager=dbmanager)
        if agent:
            return {
                "status": True,
                "message": "Agent retrieved successfully",
                "data": agent,
            }
        else:
            return {
                "status": False,
                "message": "Agent not found",
            }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving agent: " + str(ex_error),
        }

@api.post("/agents")
async def create_user_agents(req: DBWebRequestModel):
    """Create a new agent for a user"""
    try:
        agents = dbutils.upsert_agent(agent_flow_spec=req.agent, dbmanager=dbmanager)
        return {
            "status": True,
            "message": "Agent upserted successfully",
            "data": agents,
        }

    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while upserting agent: " + str(ex_error),
        }


@api.delete("/agents/delete")
async def delete_user_agent(req: DBWebRequestModel):
    """Delete an agent for a user"""

    try:
        agents = dbutils.delete_agent(agent=req.agent, dbmanager=dbmanager)

        return {
            "status": True,
            "message": "Agent deleted successfully",
            "data": agents,
        }

    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while deleting agent: " + str(ex_error),
        }



@api.get("/groups")
async def get_user_groups(user_id: str):
    try:
        groups = dbutils.get_groups(user_id, dbmanager=dbmanager)

        return {
            "status": True,
            "message": "Groups retrieved successfully",
            "data": groups,
        }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving groups: " + str(ex_error),
        }

@api.get("/group")
async def get_group(id: str):
    try:
        group = dbutils.get_group(id, dbmanager=dbmanager)
        if group:
            return {
                "status": True,
                "message": "Group retrieved successfully",
                "data": group,
            }
        else:
            return {
                "status": False,
                "message": "Group not found",
            }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving group: " + str(ex_error),
        }

@api.post("/groups")
async def create_user_groups(req: DBWebRequestModel):
    """Create a new group for a user"""
    try:
        groups = dbutils.upsert_group(group_flow_spec=req.group, dbmanager=dbmanager)
        return {
            "status": True,
            "message": "Group upserted successfully",
            "data": groups,
        }

    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while upserting group: " + str(ex_error),
        }


@api.delete("/groups/delete")
async def delete_user_group(req: DBWebRequestModel):
    """Delete an group for a user"""

    try:
        groups = dbutils.delete_group(group=req.group, dbmanager=dbmanager)

        return {
            "status": True,
            "message": "Group deleted successfully",
            "data": groups,
        }

    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while deleting group: " + str(ex_error),
        }
        
@api.get("/models")
async def get_user_models(user_id: str):
    try:
        models = dbutils.get_models(user_id, dbmanager=dbmanager)

        return {
            "status": True,
            "message": "Models retrieved successfully",
            "data": models,
        }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving models: " + str(ex_error),
        }


@api.post("/models")
async def create_user_models(req: DBWebRequestModel):
    """Create a new model for a user"""

    try:
        models = dbutils.upsert_model(model=req.model, dbmanager=dbmanager)

        return {
            "status": True,
            "message": "Model created successfully",
            "data": models,
        }

    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while creating model: " + str(ex_error),
        }


@api.post("/models/test")
async def test_user_models(req: DBWebRequestModel):
    """Test a model to verify it works"""

    try:
        response = test_model(model=req.model)
        return {
            "status": True,
            "message": "Model tested successfully",
            "data": response,
        }

    except OpenAIError as oai_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while testing model: " + str(oai_error),
        }
    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while testing model: " + str(ex_error),
        }


@api.delete("/models/delete")
async def delete_user_model(req: DBWebRequestModel):
    """Delete a model for a user"""

    try:
        models = dbutils.delete_model(model=req.model, dbmanager=dbmanager)

        return {
            "status": True,
            "message": "Model deleted successfully",
            "data": models,
        }

    except Exception as ex_error:
        print(traceback.format_exc())
        return {
            "status": False,
            "message": "Error occurred while deleting model: " + str(ex_error),
        }

@api.get("/workflow_session")
async def get_workflow_session(workflow_id: str, current_session_id: str):
    try:
        workflow_session = dbutils.get_workflow_session(workflow_id, current_session_id, dbmanager=dbmanager)
        if workflow_session:
            return {
                "status": True,
                "message": "Workflow session retrieved successfully",
                "data": workflow_session,
            }
        else:
            return {
                "status": False,
                "message": "Workflow session not found"
            }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving workflow session: " + str(ex_error),
        }

@api.post("/workflow_session")
async def upsert_workflow_session(req: UpsertWorkflowSession):
    """Upsert a new session for a workflow"""
    try:
        session = dbutils.upsert_workflow_session(workflow_id=req.workflow_id, target_session_id=req.target_session_id, current_session_id=req.current_session_id, dbmanager=dbmanager)
        if session:
            return {
                "status": True,
                "message": "Workflow session upserted successfully",
                "data": session,
            }
        else:
            return {
                "status": False,
                "message": "Workflow session not upserted"
            }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while upserting workflow session: " + str(ex_error),
        }
            
@api.get("/workflow")
async def get_workflow(id: str):
    try:
        workflow = dbutils.get_workflow(id, dbmanager=dbmanager)
        if workflow:
            return {
                "status": True,
                "message": "Workflow retrieved successfully",
                "data": workflow,
            }
        else:
            return {
                "status": False,
                "message": "Workflow not found"
            }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving workflow: " + str(ex_error),
        }
        
@api.get("/workflows")
async def get_user_workflows(user_id: str):
    try:
        workflows = dbutils.get_workflows(user_id, dbmanager=dbmanager)

        return {
            "status": True,
            "message": "Workflows retrieved successfully",
            "data": workflows,
        }
    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while retrieving workflows: " + str(ex_error),
        }


@api.post("/workflows")
async def create_user_workflow(req: DBWebRequestModel):
    """Create a new workflow for a user"""
    try:
        workflow = dbutils.upsert_workflow(workflow=req.workflow, dbmanager=dbmanager)
        return {
            "status": True,
            "message": "Workflow upserted successfully",
            "data": workflow,
        }

    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while creating workflow: " + str(ex_error),
        }


@api.delete("/workflows/delete")
async def delete_user_workflow(req: DBWebRequestModel):
    """Delete a workflow for a user"""

    try:
        workflow = dbutils.delete_workflow(workflow=req.workflow, dbmanager=dbmanager)
        return {
            "status": True,
            "message": "Workflow deleted successfully",
            "data": workflow,
        }

    except Exception as ex_error:
        print(ex_error)
        return {
            "status": False,
            "message": "Error occurred while deleting workflow: " + str(ex_error),
        }


@api.get("/version")
async def get_version():
    return {
        "status": True,
        "message": "Version retrieved successfully",
        "data": {"version": VERSION},
    }

