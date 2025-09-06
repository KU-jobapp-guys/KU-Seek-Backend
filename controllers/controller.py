"""Module containing endpoints for operations."""

from .task_controller import TaskController
from .job_controller import JobController
from typing import Dict, Optional


task_manager = TaskController()


def get_all_tasks():
    """Return Placeholder."""
    return task_manager.get_all_tasks()


def create_task(body: Dict):
    """Return Placeholder."""
    return task_manager.create_task(body)


def get_task_by_id(task_id: str) -> Optional[Dict]:
    """Return Placeholder."""
    return task_manager.get_task_by_id(task_id)


def update_task(task_id: str, body: Dict) -> Optional[Dict]:
    """Return Placeholder."""
    return task_manager.update_task(task_id, body)


def delete_task(task_id: str):
    """Return Placeholder."""
    return task_manager.delete_task(task_id)


job_manager = JobController()


def get_all_jobs():
    """Return all Jobs."""
    return job_manager.get_all_jobs()