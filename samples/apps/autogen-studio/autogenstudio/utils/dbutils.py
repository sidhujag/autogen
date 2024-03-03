import json
import logging
import sqlite3
import threading
import os
import chromadb

if chromadb.__version__ < "0.4.15":
    from chromadb.api import API
else:
    from chromadb.api import ClientAPI as API
from chromadb.api.types import QueryResult
import chromadb.utils.embedding_functions as ef
from typing import Any, List, Dict, Optional, Tuple
from ..datamodel import AgentFlowSpec, AgentWorkFlowConfig, Gallery, Message, Model, Session, Skill
from ..version import __version__ as __db_version__


VERSION_TABLE_SQL = """
            CREATE TABLE IF NOT EXISTS version (

                version TEXT NOT NULL,
                UNIQUE (version)
            )
            """

MODELS_TABLE_SQL = """
            CREATE TABLE IF NOT EXISTS models (
                id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                model TEXT,
                api_key TEXT,
                base_url TEXT,
                api_type TEXT,
                api_version TEXT,
                description TEXT,
                UNIQUE (id, user_id)
            )
            """


MESSAGES_TABLE_SQL = """
            CREATE TABLE IF NOT EXISTS messages (
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                root_msg_id TEXT NOT NULL,
                msg_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp DATETIME,
                UNIQUE (user_id, session_id, root_msg_id, msg_id)
            )
            """

SESSIONS_TABLE_SQL = """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                name TEXT,
                flow_config TEXT,
                UNIQUE (user_id, id)
            )
            """

SKILLS_TABLE_SQL = """
            CREATE TABLE IF NOT EXISTS skills (
                id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                content TEXT,
                examples TEXT,
                title TEXT,
                file_name TEXT,
                description TEXT,
                UNIQUE (id, user_id)
            )
            """
AGENTS_TABLE_SQL = """
            CREATE TABLE IF NOT EXISTS agents (

                id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                config TEXT,
                groupchat_config TEXT,
                type TEXT,
                init_code TEXT,
                skills TEXT,
                UNIQUE (id, user_id)
            )
            """
            
WORKFLOWS_TABLE_SQL = """
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                sender TEXT,
                receiver TEXT,
                type TEXT,
                name TEXT,
                description TEXT,
                summary_method TEXT,
                UNIQUE (id, user_id)
            )
            """

GALLERY_TABLE_SQL = """
            CREATE TABLE IF NOT EXISTS gallery (
                id TEXT NOT NULL,
                session TEXT,
                messages TEXT,
                tags TEXT,
                timestamp DATETIME NOT NULL,
                UNIQUE ( id)
            )
            """
            
lock = threading.Lock()
logger = logging.getLogger()


class DBManager:
    """
    A database manager class that handles the creation and interaction with an SQLite database.
    """

    def __init__(self, path: str = "database.sqlite", **kwargs: Any) -> None:
        """
        Initializes the DBManager object, creates a database if it does not exist, and establishes a connection.

        Args:
            path (str): The file path to the SQLite database file.
            **kwargs: Additional keyword arguments to pass to the sqlite3.connect method.
        """

        self.path = path
        # check if the database exists, if not create it
        # self.reset_db()
        if not os.path.exists(self.path):
            logger.info("Creating database")
            self.init_db(path=self.path, **kwargs)

        try:
            self.conn = sqlite3.connect(self.path, check_same_thread=False, **kwargs)
            self.cursor = self.conn.cursor()
            self.migrate()
        except Exception as e:
            logger.error("Error connecting to database: %s", e)
            raise e

    def migrate(self):
        """
        Run migrations to update the database schema.
        """
        self.add_column_if_not_exists("sessions", "name", "TEXT")

    def add_column_if_not_exists(self, table: str, column: str, column_type: str):
        """
        Adds a new column to the specified table if it does not exist.

        Args:
            table (str): The table name where the column should be added.
            column (str): The column name that should be added.
            column_type (str): The data type of the new column.
        """
        try:
            self.cursor.execute(f"PRAGMA table_info({table})")
            column_names = [row[1] for row in self.cursor.fetchall()]
            if column not in column_names:
                self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
                self.conn.commit()
                logger.info(f"Migration: New '{column}' column has been added to the '{table}' table.")
            else:
                logger.info(f"'{column}' column already exists in the '{table}' table.")

        except Exception as e:
            print(f"Error while checking and updating '{table}' table: {e}")

    def reset_db(self):
        """
        Reset the database by deleting the database file and creating a new one.
        """
        print("resetting db")
        if os.path.exists(self.path):
            os.remove(self.path)
        self.init_db(path=self.path)

    def init_db(self, path: str = "database.sqlite", **kwargs: Any) -> None:
        """
        Initializes the database by creating necessary tables.

        Args:
            path (str): The file path to the SQLite database file.
            **kwargs: Additional keyword arguments to pass to the sqlite3.connect method.
        """
        # Connect to the database (or create a new one if it doesn't exist)
        self.conn = sqlite3.connect(path, check_same_thread=False, **kwargs)
        self.cursor = self.conn.cursor()

        # Create the version table
        self.cursor.execute(VERSION_TABLE_SQL)
        self.cursor.execute("INSERT INTO version (version) VALUES (?)", (__db_version__,))

        # Create the models table
        self.cursor.execute(MODELS_TABLE_SQL)

        # Create the messages table
        self.cursor.execute(MESSAGES_TABLE_SQL)

        # Create a sessions table
        self.cursor.execute(SESSIONS_TABLE_SQL)

        # Create a  skills
        self.cursor.execute(SKILLS_TABLE_SQL)

        # Create a gallery table
        self.cursor.execute(GALLERY_TABLE_SQL)

        # Create a agents table
        self.cursor.execute(AGENTS_TABLE_SQL)
        
        # Create a workflows table
        self.cursor.execute(WORKFLOWS_TABLE_SQL)
        

        # init skills table with content of defaultskills.json in current directory
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(current_dir, "dbdefaults.json"), "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            skills = data["skills"]
            agents = data["agents"]
            models = data["models"]
            for model in models:
                model = Model(**model)
                self.cursor.execute(
                    "INSERT INTO models (id, user_id, timestamp, model, api_key, base_url, api_type, api_version, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        model.id,
                        "default",
                        model.timestamp,
                        model.model,
                        model.api_key,
                        model.base_url,
                        model.api_type,
                        model.api_version,
                        model.description,
                    ),
                )

            for skill in skills:
                skill = Skill(**skill)

                self.cursor.execute(
                    "INSERT INTO skills (id, user_id, timestamp, content, examples, title, file_name, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (skill.id, "default", skill.timestamp, skill.content, skill.examples, skill.title, skill.file_name, skill.description),
                )
            for agent in agents:
                agent = AgentFlowSpec(**agent)
                # Ensure groupchat_config is initialized properly
                if not hasattr(agent, 'groupchat_config') or agent.groupchat_config is None:
                    agent.groupchat_config = {}

                # When building updated_data, check if groupchat_config can call .dict()
                groupchat_config_data = agent.groupchat_config.dict() if hasattr(agent.groupchat_config, 'dict') else {}

                agent.skills = [skill.dict() for skill in agent.skills] if agent.skills else None
                self.cursor.execute(
                    "INSERT INTO agents (id, user_id, timestamp, config, groupchat_config, type, skills, init_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        agent.id,
                        "default",
                        agent.timestamp,
                        json.dumps(agent.config.dict()),
                        json.dumps(groupchat_config_data),
                        agent.type,
                        json.dumps(agent.skills),
                        agent.init_code,
                    ),
                )
                
            for workflow in data["workflows"]:
                workflow = AgentWorkFlowConfig(**workflow)
                self.cursor.execute(
                    "INSERT INTO workflows (id, user_id, timestamp, sender, receiver, type, name, description, summary_method) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)",
                    (
                        workflow.id,
                        "default",
                        workflow.timestamp,
                        json.dumps(workflow.sender.dict()),
                        json.dumps(workflow.receiver.dict()),
                        workflow.type,
                        workflow.name,
                        workflow.description,
                        workflow.summary_method,
                    ),
                )

        # Commit the changes and close the connection
        self.conn.commit()

    def query(self, query: str, args: Tuple = (), return_json: bool = False) -> List[Dict[str, Any]]:
        """
        Executes a given SQL query and returns the results.

        Args:
            query (str): The SQL query to execute.
            args (Tuple): The arguments to pass to the SQL query.
            return_json (bool): If True, the results will be returned as a list of dictionaries.

        Returns:
            List[Dict[str, Any]]: The result of the SQL query.
        """
        try:
            with lock:
                self.cursor.execute(query, args)
                result = self.cursor.fetchall()
                self.commit()
                if return_json:
                    result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]
                return result
        except Exception as e:
            logger.error("Error running query with query %s and args %s: %s", query, args, e)
            raise e

    def commit(self) -> None:
        """
        Commits the current transaction Modelto the database.
        """
        self.conn.commit()

    def close(self) -> None:
        """
        Closes the database connection.
        """
        self.conn.close()


def get_models(user_id: str, dbmanager: DBManager) -> List[dict]:
    """
    Get all models for a given user from the database.

    Args:
        user_id: The user id to get models for
        dbmanager: The DBManager instance to interact with the database

    Returns:
        A list  of model configurations
    """
    query = "SELECT * FROM models WHERE user_id = ? OR user_id = ?"
    args = (user_id, "default")
    results = dbmanager.query(query, args, return_json=True)
    return results


def upsert_model(model: Model, dbmanager: DBManager) -> List[dict]:
    """
    Insert or update a model configuration in the database.

    Args:
        model: The Model object containing model configuration data
        dbmanager: The DBManager instance to interact with the database

    Returns:
        A list  of model configurations
    """

    # Check if the model config with the provided id already exists in the database
    existing_model = get_item_by_field("models", "id", model.id, dbmanager)

    if existing_model:
        # If the model config exists, update it with the new data
        updated_data = {
            "model": model.model,
            "api_key": model.api_key,
            "base_url": model.base_url,
            "api_type": model.api_type,
            "api_version": model.api_version,
            "user_id": model.user_id,
            "timestamp": model.timestamp,
            "description": model.description,
        }
        update_item("models", model.id, updated_data, dbmanager)
    else:
        # If the model config does not exist, insert a new one
        query = """
            INSERT INTO models (id, user_id, timestamp, model, api_key, base_url, api_type, api_version, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        args = (
            model.id,
            model.user_id,
            model.timestamp,
            model.model,
            model.api_key,
            model.base_url,
            model.api_type,
            model.api_version,
            model.description,
        )
        dbmanager.query(query=query, args=args)

    # Return the inserted or updated model config
    models = get_models(model.user_id, dbmanager)
    return models


def delete_model(model: Model, dbmanager: DBManager) -> List[dict]:
    """
    Delete a model configuration from the database where id = model.id and user_id = model.user_id.

    Args:
        model: The Model object containing model configuration data
        dbmanager: The DBManager instance to interact with the database

    Returns:
        A list  of model configurations
    """

    query = "DELETE FROM models WHERE id = ? AND user_id = ?"
    args = (model.id, model.user_id)
    dbmanager.query(query=query, args=args)

    # Return the remaining model configs
    models = get_models(model.user_id, dbmanager)
    return models


def create_message(message: Message, dbmanager: DBManager) -> None:
    """
    Save a message in the database using the provided database manager.

    :param message: The Message object containing message data
    :param dbmanager: The DBManager instance used to interact with the database
    """
    query = "INSERT INTO messages (user_id, root_msg_id, msg_id, role, content, metadata, timestamp, session_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    args = (
        message.user_id,
        message.root_msg_id,
        message.msg_id,
        message.role,
        message.content,
        message.metadata,
        message.timestamp,
        message.session_id,
    )
    dbmanager.query(query=query, args=args)


def get_messages(user_id: str, session_id: str, dbmanager: DBManager) -> List[dict]:
    """
    Load messages for a specific user and session from the database, sorted by timestamp.

    :param user_id: The ID of the user whose messages are to be loaded
    :param session_id: The ID of the session whose messages are to be loaded
    :param dbmanager: The DBManager instance to interact with the database

    :return: A list of dictionaries, each representing a message
    """
    query = "SELECT * FROM messages WHERE user_id = ? AND session_id = ?"
    args = (user_id, session_id)
    result = dbmanager.query(query=query, args=args, return_json=True)
    # Sort by timestamp ascending
    result = sorted(result, key=lambda k: k["timestamp"], reverse=False)
    return result


def get_sessions(user_id: str, dbmanager: DBManager) -> List[dict]:
    """
    Load sessions for a specific user from the database, sorted by timestamp.

    :param user_id: The ID of the user whose sessions are to be loaded
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of dictionaries, each representing a session
    """
    query = "SELECT * FROM sessions WHERE user_id = ?"
    args = (user_id,)
    result = dbmanager.query(query=query, args=args, return_json=True)
    # Sort by timestamp ascending
    result = sorted(result, key=lambda k: k["timestamp"], reverse=True)
    for row in result:
        row["flow_config"] = json.loads(row["flow_config"])
    return result


def get_session(id: str, dbmanager: DBManager) -> List[dict]:
    existing_session = get_item_by_field("sessions", "id", id, dbmanager)
    if existing_session:
        existing_session["flow_config"] = json.loads(existing_session["flow_config"])
        return existing_session
    return None

def create_session(user_id: str, session: Session, dbmanager: DBManager) -> List[dict]:
    """
    Create a new session for a specific user in the database.

    :param user_id: The ID of the user whose session is to be created
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of dictionaries, each representing a session
    """
    query = "INSERT INTO sessions (user_id, id, timestamp, flow_config) VALUES (?, ?, ?, ?)"
    args = (session.user_id, session.id, session.timestamp, json.dumps(session.flow_config.dict()))
    dbmanager.query(query=query, args=args)
    sessions = get_sessions(user_id=user_id, dbmanager=dbmanager)

    return sessions


def rename_session(name: str, session: Session, dbmanager: DBManager) -> List[dict]:
    """
    Edit a session for a specific user in the database.

    :param name: The new name of the session
    :param session: The Session object containing session data
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of dictionaries, each representing a session
    """

    query = "UPDATE sessions SET name = ? WHERE id = ?"
    args = (name, session.id)
    dbmanager.query(query=query, args=args)
    sessions = get_sessions(user_id=session.user_id, dbmanager=dbmanager)

    return sessions


def delete_session(session: Session, dbmanager: DBManager) -> List[dict]:
    """
    Delete a specific session  and all messages for that session in the database.

    :param session: The Session object containing session data
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of the remaining sessions
    """

    query = "DELETE FROM sessions WHERE id = ?"
    args = (session.id,)
    dbmanager.query(query=query, args=args)

    query = "DELETE FROM messages WHERE session_id = ?"
    args = (session.id,)
    dbmanager.query(query=query, args=args)

    return get_sessions(user_id=session.user_id, dbmanager=dbmanager)


def create_gallery(session: Session, dbmanager: DBManager, tags: List[str] = []) -> Gallery:
    """
    Publish a session to the gallery table in the database. Fetches the session messages first, then saves session and messages object to the gallery database table.
    :param session: The Session object containing session data
    :param dbmanager: The DBManager instance used to interact with the database
    :param tags: A list of tags to associate with the session
    :return: A gallery object containing the session and messages objects
    """

    messages = get_messages(user_id=session.user_id, session_id=session.id, dbmanager=dbmanager)
    gallery_item = Gallery(session=session, messages=messages, tags=tags)
    query = "INSERT INTO gallery (id, session, messages, tags, timestamp) VALUES (?, ?, ?, ?,?)"
    args = (
        gallery_item.id,
        json.dumps(gallery_item.session.dict()),
        json.dumps([message.dict() for message in gallery_item.messages]),
        json.dumps(gallery_item.tags),
        gallery_item.timestamp,
    )
    dbmanager.query(query=query, args=args)
    return gallery_item


def get_gallery(gallery_id, dbmanager: DBManager) -> List[Gallery]:
    """
    Load gallery items from the database, sorted by timestamp. If gallery_id is provided, only the gallery item with the matching gallery_id will be returned.

    :param gallery_id: The ID of the gallery item to be loaded
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of Gallery objects
    """

    if gallery_id:
        query = "SELECT * FROM gallery WHERE id = ?"
        args = (gallery_id,)
    else:
        query = "SELECT * FROM gallery"
        args = ()
    result = dbmanager.query(query=query, args=args, return_json=True)
    # Sort by timestamp ascending
    result = sorted(result, key=lambda k: k["timestamp"], reverse=True)
    gallery = []
    for row in result:
        gallery_item = Gallery(
            id=row["id"],
            session=Session(**json.loads(row["session"])),
            messages=[Message(**message) for message in json.loads(row["messages"])],
            tags=json.loads(row["tags"]),
            timestamp=row["timestamp"],
        )
        gallery.append(gallery_item)
    return gallery


def get_skills(user_id: str, dbmanager: DBManager) -> List[Skill]:
    """
    Load skills from the database, sorted by timestamp. Load skills where id = user_id or user_id = default.

    :param user_id: The ID of the user whose skills are to be loaded
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of Skill objects
    """

    query = "SELECT * FROM skills WHERE user_id = ? OR user_id = ?"
    args = (user_id, "default")
    result = dbmanager.query(query=query, args=args, return_json=True)
    # Sort by timestamp ascending
    result = sorted(result, key=lambda k: k["timestamp"], reverse=True)
    skills = []
    for row in result:
        skill = Skill(**row)
        skills.append(skill)
    return skills


def search_vec_db(documents, ids, objects, queries):
    # Initialize the semantic search client
    search_client = chromadb.Client()
    embedding_function = ef.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
    collection_name = "collection"
    collection = search_client.create_collection(name=collection_name, embedding_function=embedding_function)
    collection.add(documents=documents, ids=ids)
    list_returned = {}  # Dictionary to hold query results
    added_ids = set()  # Set to track added IDs
    nresults = 5
    count = collection.count()
    if count < nresults:
        nresults = count
    # Perform the queries and populate the dictionary
    for query in queries:
        list_returned[query] = []  # Initialize list for this query
        results = collection.query(query_texts=[query], n_results=nresults)

        # Assuming 'results' structure contains 'ids' as first item in a nested list
        result_ids = results['ids'][0] if results['ids'] else []
        for result_id in result_ids:
            # Check if ID has already been added
            if result_id not in added_ids:
                matching_object = next((object for object in objects if object.id == result_id), None)
                if matching_object:
                    list_returned[query].append(matching_object)
                    added_ids.add(result_id)  # Mark this ID as added

    search_client.delete_collection(collection_name)
    return list_returned

def discover_services(service_type: str, user_id: str, queries: List[str], dbmanager: DBManager) -> Dict[str, List[Any]]:
    """
    Discover agents using semantic search and return a dictionary mapping each query to a list of relevant agents.
    """
    if service_type == "agents":
        objs = get_agents(user_id, dbmanager)

        documents = [
            "name: " + (agent.config.name if agent.config.name is not None else "No Title") + "\n\ndescription: " + (agent.config.description if agent.config.description is not None else "No Description")
            for agent in objs
        ]

        ids = [agent.id for agent in objs]
    elif service_type == "skills":
        objs = get_skills(user_id, dbmanager)

        documents = [
            "title: " + (skill.title if skill.title is not None else "No Title") + "\n\ncontent: "  + "\n\ndescription: " + (skill.description if skill.description is not None else "No Description")
            for skill in objs
        ]
        ids = [skill.id for skill in objs]
    return search_vec_db(documents, ids, objs, queries)

def get_skill(id: str, dbmanager: DBManager) -> Skill:
    existing_skill = get_item_by_field("skills", "id", id, dbmanager)
    if existing_skill:
        skill = Skill(**existing_skill)
        return skill
    return None

def upsert_skill(skill: Skill, dbmanager: DBManager) -> List[Skill]:
    """
    Insert or update a skill for a specific user in the database.

    If the skill with the given ID already exists, it will be updated with the new data.
    Otherwise, a new skill will be created.

    :param  skill: The Skill object containing skill data
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of dictionaries, each representing a skill
    """

    existing_skill = get_item_by_field("skills", "id", skill.id, dbmanager)

    if existing_skill:
        updated_data = {
            "user_id": skill.user_id,
            "timestamp": skill.timestamp,
            "content": skill.content,
            "examples": skill.examples,
            "title": skill.title,
            "file_name": skill.file_name,
            "description": skill.description,
        }
        update_item("skills", skill.id, updated_data, dbmanager)
    else:
        query = "INSERT INTO skills (id, user_id, timestamp, content, examples, title, file_name, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        args = (skill.id, skill.user_id, skill.timestamp, skill.content, skill.examples, skill.title, skill.file_name, skill.description)
        dbmanager.query(query=query, args=args)

    skills = get_skills(user_id=skill.user_id, dbmanager=dbmanager)

    return skills


def delete_skill(skill: Skill, dbmanager: DBManager) -> List[Skill]:
    """
    Delete a skill for a specific user in the database.

    :param  skill: The Skill object containing skill data
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of dictionaries, each representing a skill
    """
    # delete where id = skill.id and user_id = skill.user_id
    query = "DELETE FROM skills WHERE id = ? AND user_id = ?"
    args = (skill.id, skill.user_id)
    dbmanager.query(query=query, args=args)

    return get_skills(user_id=skill.user_id, dbmanager=dbmanager)


def delete_message(
    user_id: str, msg_id: str, session_id: str, dbmanager: DBManager, delete_all: bool = False
) -> List[dict]:
    """
    Delete a specific message or all messages for a user and session from the database.

    :param user_id: The ID of the user whose messages are to be deleted
    :param msg_id: The ID of the specific message to be deleted (ignored if delete_all is True)
    :param session_id: The ID of the session whose messages are to be deleted
    :param dbmanager: The DBManager instance to interact with the database
    :param delete_all: If True, all messages for the user will be deleted
    :return: A list of the remaining messages if not all were deleted, otherwise an empty list
    """

    if delete_all:
        query = "DELETE FROM messages WHERE user_id = ? AND session_id = ?"
        args = (user_id, session_id)
        dbmanager.query(query=query, args=args)
        return []
    else:
        query = "DELETE FROM messages WHERE user_id = ? AND msg_id = ? AND session_id = ?"
        args = (user_id, msg_id, session_id)
        dbmanager.query(query=query, args=args)
        messages = get_messages(user_id=user_id, session_id=session_id, dbmanager=dbmanager)
        return messages


def get_agents(user_id: str, dbmanager: DBManager) -> List[AgentFlowSpec]:
    """
    Load agents from the database, sorted by timestamp. Load agents where id = user_id or user_id = default.

    :param user_id: The ID of the user whose agents are to be loaded
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of AgentFlowSpec objects
    """

    query = "SELECT * FROM agents WHERE user_id = ? OR user_id = ?"
    args = (user_id, "default")
    result = dbmanager.query(query=query, args=args, return_json=True)
    # Sort by timestamp ascending
    result = sorted(result, key=lambda k: k["timestamp"], reverse=True)
    agents = []
    for row in result:
        row["config"] = json.loads(row["config"])
        row["groupchat_config"] = json.loads(row["groupchat_config"])
        row["skills"] = json.loads(row["skills"] or "[]")
        agent = AgentFlowSpec(**row)
        agents.append(agent)
    return agents

def get_agent(id: str, dbmanager: DBManager) -> AgentFlowSpec:
    """
    Find agent by id

    :param id: The ID of the agent
    :param dbmanager: The DBManager instance to interact with the database
    :return: A AgentFlowSpec object
    """

    existing_agent = get_item_by_field("agents", "id", id, dbmanager)
    if existing_agent:
        existing_agent["config"] = json.loads(existing_agent["config"])
        existing_agent["groupchat_config"] = json.loads(existing_agent["groupchat_config"])
        existing_agent["skills"] = json.loads(existing_agent["skills"] or "[]")
        agent = AgentFlowSpec(**existing_agent)
        return agent
    return None

def upsert_agent(agent_flow_spec: AgentFlowSpec, dbmanager: DBManager) -> List[AgentFlowSpec]:
    """
    Insert or update an agent for a specific user in the database.

    If the agent with the given ID already exists, it will be updated with the new data.
    Otherwise, a new agent will be created.

    :param agent_flow_spec: The AgentFlowSpec object containing agent configuration
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of dictionaries, each representing an agent after insertion or update
    """

    existing_agent = get_item_by_field("agents", "id", agent_flow_spec.id, dbmanager)
    # Ensure groupchat_config is initialized properly
    if not hasattr(agent_flow_spec, 'groupchat_config') or agent_flow_spec.groupchat_config is None:
        agent_flow_spec.groupchat_config = {}

    # When building updated_data, check if groupchat_config can call .dict()
    groupchat_config_data = agent_flow_spec.groupchat_config.dict() if hasattr(agent_flow_spec.groupchat_config, 'dict') else {}

    if existing_agent:
        updated_data = {
            "user_id": agent_flow_spec.user_id,
            "timestamp": agent_flow_spec.timestamp,
            "config": json.dumps(agent_flow_spec.config.dict()),
            "groupchat_config": json.dumps(groupchat_config_data),
            "type": agent_flow_spec.type,
            "init_code": agent_flow_spec.init_code,
            "skills": json.dumps([x.dict() for x in agent_flow_spec.skills] if agent_flow_spec.skills else []),
        }
        update_item("agents", agent_flow_spec.id, updated_data, dbmanager)
    else:
        query = "INSERT INTO agents (id, user_id, timestamp, config, groupchat_config, type, skills, init_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        config_json = json.dumps(agent_flow_spec.config.dict())
        args = (
            agent_flow_spec.id,
            agent_flow_spec.user_id,
            agent_flow_spec.timestamp,
            config_json,
            json.dumps(groupchat_config_data),
            agent_flow_spec.type,
            json.dumps([x.dict() for x in agent_flow_spec.skills] if agent_flow_spec.skills else []),
            agent_flow_spec.init_code,
        )
        dbmanager.query(query=query, args=args)

    agents = get_agents(user_id=agent_flow_spec.user_id, dbmanager=dbmanager)
    return agents


def delete_agent(agent: AgentFlowSpec, dbmanager: DBManager) -> List[AgentFlowSpec]:
    """
    Delete an agent for a specific user from the database.

    :param agent: The AgentFlowSpec object containing agent configuration
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of dictionaries, each representing an agent after deletion
    """

    # delete based on agent.id and agent.user_id
    query = "DELETE FROM agents WHERE id = ? AND user_id = ?"
    args = (agent.id, agent.user_id)
    dbmanager.query(query=query, args=args)

    return get_agents(user_id=agent.user_id, dbmanager=dbmanager)

def get_item_by_field(table: str, field: str, value: Any, dbmanager: DBManager) -> Optional[Dict[str, Any]]:
    query = f"SELECT * FROM {table} WHERE {field} = ?"
    args = (value,)
    result = dbmanager.query(query=query, args=args, return_json=True)
    return result[0] if result else None


def update_item(table: str, item_id: str, updated_data: Dict[str, Any], dbmanager: DBManager) -> None:
    set_clause = ", ".join([f"{key} = ?" for key in updated_data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
    args = (*updated_data.values(), item_id)
    dbmanager.query(query=query, args=args)


def get_workflows(user_id: str, dbmanager: DBManager) -> List[AgentWorkFlowConfig]:
    """
    Load workflows for a specific user from the database, sorted by timestamp.

    :param user_id: The ID of the user whose workflows are to be loaded
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of dictionaries, each representing a workflow
    """
    query = "SELECT * FROM workflows WHERE user_id = ? OR user_id = ?"
    args = (user_id, "default")
    result = dbmanager.query(query=query, args=args, return_json=True)
    # Sort by timestamp ascending
    result = sorted(result, key=lambda k: k["timestamp"], reverse=True)
    workflows = []
    for row in result:
        row["sender"] = json.loads(row["sender"])
        row["receiver"] = json.loads(row["receiver"])
        workflow = AgentWorkFlowConfig(**row)
        workflows.append(workflow)
    return workflows

def upsert_workflow(workflow: AgentWorkFlowConfig, dbmanager: DBManager) -> List[AgentWorkFlowConfig]:
    """
    Insert or update a workflow for a specific user in the database.

    If the workflow with the given ID already exists, it will be updated with the new data.
    Otherwise, a new workflow will be created.

    :param workflow: The AgentWorkFlowConfig object containing workflow data
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of dictionaries, each representing a workflow after insertion or update
    """
    existing_workflow = get_item_by_field("workflows", "id", workflow.id, dbmanager)

    # print(workflow.receiver)

    if existing_workflow:
        updated_data = {
            "user_id": workflow.user_id,
            "timestamp": workflow.timestamp,
            "sender": json.dumps(workflow.sender.dict()),
            "receiver": json.dumps(
                [receiver.dict() for receiver in workflow.receiver]
                if isinstance(workflow.receiver, list)
                else workflow.receiver.dict()
            ),
            "type": workflow.type,
            "name": workflow.name,
            "description": workflow.description,
            "summary_method": workflow.summary_method,
        }
        update_item("workflows", workflow.id, updated_data, dbmanager)
    else:
        query = "INSERT INTO workflows (id, user_id, timestamp, sender, receiver, type, name, description, summary_method) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        args = (
            workflow.id,
            workflow.user_id,
            workflow.timestamp,
            json.dumps(workflow.sender.dict()),
            json.dumps(
                [receiver.dict() for receiver in workflow.receiver]
                if isinstance(workflow.receiver, list)
                else workflow.receiver.dict()
            ),
            workflow.type,
            workflow.name,
            workflow.description,
            workflow.summary_method,
        )
        dbmanager.query(query=query, args=args)

    return get_workflows(user_id=workflow.user_id, dbmanager=dbmanager)


def delete_workflow(workflow: AgentWorkFlowConfig, dbmanager: DBManager) -> List[AgentWorkFlowConfig]:
    """
    Delete a workflow for a specific user from the database. If the workflow does not exist, do nothing.

    :param workflow: The AgentWorkFlowConfig object containing workflow data
    :param dbmanager: The DBManager instance to interact with the database
    :return: A list of dictionaries, each representing a workflow after deletion
    """

    # delete where workflow.id =id and workflow.user_id = user_id

    query = "DELETE FROM workflows WHERE id = ? AND user_id = ?"
    args = (workflow.id, workflow.user_id)
    dbmanager.query(query=query, args=args)

    return get_workflows(user_id=workflow.user_id, dbmanager=dbmanager)
