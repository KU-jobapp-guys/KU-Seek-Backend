"""Module containing endpoints for operations."""

from .task_controller import TaskController
from .user_profile_controller import ProfileController
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


profile_manager = ProfileController()

def create_profile(user_id:str, body: Dict) -> Optional[Dict]:
    """Add UserProfile to the database."""
    return profile_manager.create_profile(user_id, body)

    
def update_profile(user_id:str, body: Dict) -> Optional[Dict]:
    """Update User Profile data."""
    return profile_manager.update_profile(user_id, body)