"""Module containing endpoints for operations."""

from flask import request
from .task_controller import TaskController
from .user_profile_controller import ProfileController
from .job_app_controller import JobApplicationController
from .auth_controller import get_auth_user_id

from typing import Dict, Optional
from flask import current_app


def get_all_tasks():
    """Return Placeholder."""
    task_manager = TaskController(current_app.config["Database"])
    return task_manager.get_all_tasks()


def create_task(body: Dict):
    """Return Placeholder."""
    task_manager = TaskController(current_app.config["Database"])
    return task_manager.create_task(body)


def get_task_by_id(task_id: str) -> Optional[Dict]:
    """Return Placeholder."""
    task_manager = TaskController(current_app.config["Database"])
    return task_manager.get_task_by_id(task_id)


def update_task(task_id: str, body: Dict) -> Optional[Dict]:
    """Return Placeholder."""
    task_manager = TaskController(current_app.config["Database"])
    return task_manager.update_task(task_id, body)


def delete_task(task_id: str):
    """Return Placeholder."""
    task_manager = TaskController(current_app.config["Database"])
    return task_manager.delete_task(task_id)


profile_manager = ProfileController()


def get_user_profile(user_id: str) -> Dict:
    """GET UserProfile from the database."""
    return profile_manager.get_profile_by_uid(user_id)


def create_profile(body: Dict) -> Optional[Dict]:
    """Add UserProfile to the database."""
    return profile_manager.create_profile(get_auth_user_id(request), body)


def update_profile(body: Dict) -> Optional[Dict]:
    """Update User Profile data."""
    return profile_manager.update_profile(get_auth_user_id(request), body)


def create_job_application(body, job_id: int) -> Optional[Dict]:
    """Create a job application in the database."""
    app_manager = JobApplicationController(current_app.config["Database"])
    return app_manager.create_job_application(body, job_id)


def fetch_user_job_applications() -> Optional[Dict]:
    """Fetch all job applications created by the current user."""
    app_manager = JobApplicationController(current_app.config["Database"])
    return app_manager.fetch_user_job_applications()


def fetch_job_applications_from_job(job_id: int) -> Optional[Dict]:
    """Fetch all job applications related to a job post by job ID."""
    app_manager = JobApplicationController(current_app.config["Database"])
    return app_manager.fetch_job_application_from_job_post(job_id)
