"""Module containing endpoints for operations."""

from .task_controller import TaskController
from .job_controller import JobController
from typing import Dict, Optional, List



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


def get_all_jobs() -> List[Dict]:
    """Return all Jobs."""
    return job_manager.get_all_jobs()

def get_filtered_jobs(body: Dict) -> List[Dict]:
    """Return filtered Jobs."""
    return job_manager.get_filtered_job(body)

def get_applied_jobs(user_id: str) -> List[Dict]:
    """Return applied Jobs."""  
    return job_manager.get_applied_jobs(user_id)

def get_bookmark_jobs(user_id: str) -> List[Dict]:
    """Return bookmark Jobs."""  
    return job_manager.get_bookmark_jobs(user_id)
