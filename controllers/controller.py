"""Module containing endpoints for operations."""

from flask import request, jsonify
from .task_controller import TaskController
from .user_profile_controller import ProfileController
from .job_app_controller import JobApplicationController
from .auth_controller import get_auth_user_id
from .job_controller import JobController
from typing import Dict, Optional
from flask import current_app
from .education_controller import EducationController


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
    try:
        profile_manager = ProfileController(current_app.config["Database"])
        profile_data = profile_manager.get_profile_by_uid(user_id)
        return jsonify(profile_data), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def create_profile(body: Dict) -> Optional[Dict]:
    """Add UserProfile to the database."""
    try:
        profile_manager = ProfileController(current_app.config["Database"])
        new_profile = profile_manager.create_profile(get_auth_user_id(request), body)
        return jsonify(new_profile), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def update_profile(body: Dict) -> Optional[Dict]:
    """Update User Profile data."""
    try:
        profile_manager = ProfileController(current_app.config["Database"])
        profile_updated_data = profile_manager.update_profile(
            get_auth_user_id(request), body
        )

        return jsonify(profile_updated_data), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


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


def get_educations(education_id: int = None):
    """Return all educations or a single education by id."""
    try:
        education_manager = EducationController(current_app.config["Database"])
        data = education_manager.get_educations(education_id)
        return jsonify(data), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def post_education(body: Dict):
    """Create a new education record."""
    try:
        education_manager = EducationController(current_app.config["Database"])
        new_edu = education_manager.post_education(body)
        return jsonify(new_edu), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def patch_education(education_id: int, body: Dict):
    """Update an education record partially."""
    try:
        education_manager = EducationController(current_app.config["Database"])
        updated = education_manager.patch_education(education_id, body)
        return jsonify(updated), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def delete_education(education_id: int):
    """Delete an education record."""
    try:
        education_manager = EducationController(current_app.config["Database"])
        deleted = education_manager.delete_education(education_id)
        return jsonify(deleted), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500
