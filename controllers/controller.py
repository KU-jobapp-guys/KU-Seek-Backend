"""Module containing endpoints for operations."""

from flask import request, jsonify
from .task_controller import TaskController
from .user_profile_controller import ProfileController
from .auth_controller import get_auth_user_id
from .job_controller import JobController
from typing import Dict, Optional
from flask import current_app


def get_all_tasks():
    """Return all tasks."""
    task_manager = TaskController(current_app.config["Database"])
    return task_manager.get_all_tasks()


def create_task(body: Dict):
    """Create a new task."""
    task_manager = TaskController(current_app.config["Database"])
    return task_manager.create_task(body)


def get_task_by_id(task_id: str) -> Optional[Dict]:
    """Get task by ID."""
    task_manager = TaskController(current_app.config["Database"])
    return task_manager.get_task_by_id(task_id)


def update_task(task_id: str, body: Dict) -> Optional[Dict]:
    """Update task."""
    task_manager = TaskController(current_app.config["Database"])
    return task_manager.update_task(task_id, body)


def delete_task(task_id: str):
    """Delete task."""
    task_manager = TaskController(current_app.config["Database"])
    return task_manager.delete_task(task_id)


def get_user_profile(user_id: str) -> Dict:
    """GET UserProfile from the database."""
    profile_manager = ProfileController(current_app.config["Database"])
    return profile_manager.get_profile_by_uid(user_id)


def create_profile(body: Dict) -> Optional[Dict]:
    """Add UserProfile to the database."""
    profile_manager = ProfileController(current_app.config["Database"])
    return profile_manager.create_profile(get_auth_user_id(request), body)


def update_profile(body: Dict) -> Optional[Dict]:
    """Update User Profile data."""
    profile_manager = ProfileController(current_app.config["Database"])
    return profile_manager.update_profile(get_auth_user_id(request), body)


def get_all_jobs(job_id: str = ""):
    """Return all Jobs."""
    try:
        job_manager = JobController(current_app.config["Database"])
        jobs = job_manager.get_all_jobs(job_id)
        return jsonify(jobs), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def post_job(body: Dict):
    """Add new Job."""
    try:
        job_manager = JobController(current_app.config["Database"])
        new_job = job_manager.post_job(get_auth_user_id(request), body)
        return jsonify(new_job), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def get_filtered_jobs(body: Dict):
    """Return filtered Jobs."""
    try:
        job_manager = JobController(current_app.config["Database"])
        filtered_jobs = job_manager.get_filtered_job(body)
        return jsonify(filtered_jobs), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def get_bookmark_jobs():
    """Return bookmark Jobs."""
    try:
        job_manager = JobController(current_app.config["Database"])
        bookmarked_jobs = job_manager.get_bookmark_jobs(get_auth_user_id(request))
        return jsonify(bookmarked_jobs), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def post_bookmark_jobs(body: Dict):
    """Add new bookmark."""
    try:
        job_manager = JobController(current_app.config["Database"])
        bookmarked_jobs = job_manager.post_bookmark_jobs(
            get_auth_user_id(request), body
        )
        return jsonify(bookmarked_jobs), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def delete_bookmark_jobs(job_id: int):
    """Delete a bookmark."""
    try:
        user_id = get_auth_user_id(request)
        job_manager = JobController(current_app.config["Database"])
        deleted_bookmark = job_manager.delete_bookmark_jobs(user_id, job_id)
        return jsonify(deleted_bookmark), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500
