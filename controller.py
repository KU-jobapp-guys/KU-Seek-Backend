"""Module for handing API path logic."""

import sys
import pymysql
from dbutils.pooled_db import PooledDB
from decouple import config
from typing import List, Dict, Optional


OPENAPI_STUB_DIR = config("OPENAPI_STUB_DIR", default="swagger_server")

sys.path.append(OPENAPI_STUB_DIR)

pool = PooledDB(
    creator=pymysql,
    host=config("DB_HOST", default="127.0.0.1"),
    port=config("DB_PORT", cast=int, default="1234"),
    user=config("DB_USER", default="root"),
    password=config("DB_PASSWORD", default="mysecrtpw123"),
    database=config("DB_NAME", default="defaultdb"),
    maxconnections=1,
    connect_timeout=10,
    blocking=True,
)
try:
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    completed BOOLEAN DEFAULT FALSE
                );
            """)
            conn.commit()
    print("Database initialized")
except Exception as e:
    print(f"Error initializing database pool: {e}")


def execute_query(
    query: str,
    params: tuple = None,
    fetchone: bool = False,
    fetchall: bool = False,
    commit=False,
):
    """
    Convienience method for executing queries.

    Executes a given SQL query using a connection from the pool.
    Handles connection management, commits, rollbacks, and error logging.

    Args:
        query: The SQL query string to execute.
        params: A tuple of parameters to pass to the query. Defaults to None.
        fetchone: If True, fetches a single row. Defaults to False.
        fetchall: If True, fetches all rows. Defaults to False.
        commit: If true, commits the query to modify the table.

    Returns: Fetched data (dict for one, list of dicts for all)
             or None for DML operations.
    Raises:
        Exception: Re-raises any database-related exceptions after logging.
    """
    conn = None
    cursor = None
    try:
        conn = pool.connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params)
        if commit:
            conn.commit()

        if fetchone:
            return cursor.fetchone()
        elif fetchall:
            return cursor.fetchall()
        return {"message": "Query executed"}
    except Exception as e:
        print(f"Database error during query execution: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_all_tasks() -> List[Dict]:
    """
    Return all tasks in the tasks table.

    Retrieves all tasks from the MySQL database.
    Corresponds to: GET /api/v1/test/tasks
    """
    query = "SELECT * FROM tasks;"
    return execute_query(query, fetchall=True)


def create_task(body: Dict) -> Dict:
    """
    Create a new task from the request body.

    Creates a new task and inserts it into the MySQL database.
    Corresponds to: POST /api/v1/test/tasks

    Args:
        body: A request body containing task information,
                          expected to have a 'name' field and optionally 'completed'.
                          Example: {"name": "Buy groceries", "completed": false}

    Returns:
        Dict: a response message on a sucessful create operation.
    """
    if "name" not in body:
        raise ValueError("Task data must contain a 'name' field.")

    name = body["name"]
    completed = False

    query = f"INSERT INTO tasks (name, completed) VALUES ('{name}', {completed});"
    return execute_query(query, commit=True)


def get_task_by_id(task_id: str) -> Optional[Dict]:
    """
    Return a task in the database with the corresponding id.

    Retrieves a single task by its unique ID from the MySQL database.
    Corresponds to: GET /api/v1/test/tasks/{id}

    Args:
        task_id: The unique ID of the task to retrieve.

    Returns: The task dictionary if found, otherwise None.
    """
    query = f"SELECT * FROM tasks WHERE id = {task_id};"
    return execute_query(query, fetchone=True)


def update_task(task_id: str, body: Dict) -> Optional[Dict]:
    """
    Update a task in the database.

    Updates an existing task identified by its ID in the MySQL database.
    Corresponds to: PUT /api/v1/test/tasks/{id}.

    Args:
        task_id: The unique ID of the task to update.
        body: A dictionary containing the updated task information.
                          Fields like 'name' and 'completed' can be updated.

    Returns: The updated task dictionary if found and updated, otherwise None.
    """
    update_fields = []

    if "name" in body:
        update_fields.append(f"""name = '{body['name']}'""")
    if "completed" in body:
        update_fields.append(f"completed = {body['completed']}")

    if not update_fields:
        return get_task_by_id(task_id)

    query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = {task_id};"

    execute_query(query, commit=True)
    return get_task_by_id(task_id)


def delete_task(task_id: str) -> bool:
    """
    Delete a task in the database.

    Deletes a task identified by its ID from the MySQL database.
    Corresponds to: DELETE /api/v1/test/tasks/{id}.

    Args:
        task_id: The unique ID of the task to delete.

    Returns: True if the task was found and deleted, False otherwise.
    """
    existing_task = get_task_by_id(task_id)
    if not existing_task:
        return False

    query = f"DELETE FROM tasks WHERE id = {task_id};"
    execute_query(query, commit=True)
    return existing_task
