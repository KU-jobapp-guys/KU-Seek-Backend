"""Module for handing API path logic."""

from typing import List, Dict, Optional
from .models.task_model import Task
from .decorators import role_required

class TaskController:
    """Controller to use CRUD operations for tasks."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    @role_required(["Student", "Company"])
    def get_all_tasks(self) -> List[Dict]:
        """
        Return all tasks in the tasks table.

        Retrieves all tasks from the MySQL database.
        Corresponds to: GET /api/v1/test/tasks
        """
        session = self.db.get_session()
        tasks = session.query(Task).all()
        session.close()
        return [task.to_dict() for task in tasks]

    def create_task(self, body: Dict) -> Dict:
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

        session = self.db.get_session()
        task = Task(name=name)
        # add the task and commit to save to db
        session.add(task)
        session.commit()
        new_task = task.to_dict()
        session.close()
        return new_task

    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """
        Return a task in the database with the corresponding id.

        Retrieves a single task by its unique ID from the MySQL database.
        Corresponds to: GET /api/v1/test/tasks/{id}

        Args:
            task_id: The unique ID of the task to retrieve.

        Returns: The task dictionary if found, otherwise None.
        """
        session = self.db.get_session()
        task = session.query(Task).where(Task.id == task_id).one_or_none()
        if not task:
            session.close()
            return
        task = task.to_dict()
        session.close()
        return task

    def update_task(self, task_id: str, body: Dict) -> Optional[Dict]:
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
            update_fields.append(f"""name = '{body["name"]}'""")
        if "completed" in body:
            update_fields.append(f"completed = {body['completed']}")

        if not update_fields:
            return self.get_task_by_id(task_id)

        session = self.db.get_session()
        task = session.query(Task).where(Task.id == task_id).one()

        if "name" in body:
            task.name = body["name"]
        if "completed" in body:
            task.completed = body["completed"]

        session.commit()
        session.close()

        return self.get_task_by_id(task_id)

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task in the database.

        Deletes a task identified by its ID from the MySQL database.
        Corresponds to: DELETE /api/v1/test/tasks/{id}.

        Args:
            task_id: The unique ID of the task to delete.

        Returns: True if the task was found and deleted, False otherwise.
        """
        existing_task = self.get_task_by_id(task_id)
        if not existing_task:
            return False

        session = self.db.get_session()
        task = session.query(Task).where(Task.id == task_id).one()
        session.delete(task)
        session.commit()
        session.close()

        return existing_task
