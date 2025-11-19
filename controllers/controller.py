"""Module containing endpoints for operations."""

from flask import request, jsonify, Response
from .task_controller import TaskController
from .user_profile_controller import ProfileController
from .job_app_controller import JobApplicationController
from .auth_controller import get_auth_user_id
from connexion.exceptions import ProblemException
from .job_controller import JobController
from .professor_controller import ProfessorController
from .file_controller import FileController
from typing import Dict, Optional
from flask import current_app
from .skills_controller import SkillsController


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
    
def get_user_setting() -> Dict:
    """GET user setting from the database."""
    try:
        profile_manager = ProfileController(current_app.config["Database"])
        setting_data = profile_manager.get_user_setting(get_auth_user_id(request))
        return jsonify(setting_data), 200
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
    except ProblemException:
        raise
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def get_filtered_jobs(body: Dict):
    """Return filtered Jobs."""
    try:
        job_manager = JobController(current_app.config["Database"])
        if body.get("isOwner"):
            body.pop("isOwner")
            body["userId"] = get_auth_user_id(request)
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


def get_professor_connection():
    """Return professor connection."""
    try:
        user_id = get_auth_user_id(request)
        connection_controller = ProfessorController(current_app.config["Database"])
        professor_connection = connection_controller.get_connection(user_id)
        return jsonify(professor_connection), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def post_new_connection(body: dict):
    """Add new connection to the database."""
    try:
        connection_controller = ProfessorController(current_app.config["Database"])
        new_connection = connection_controller.post_connection(
            get_auth_user_id(request), body
        )
        return jsonify(new_connection), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def delete_connection(connection_id: int):
    """Delete connection from the ProfessorConnection table."""
    try:
        user_id = get_auth_user_id(request)
        connection_controller = ProfessorController(current_app.config["Database"])
        deleted_connection = connection_controller.delete_connection(
            user_id, connection_id
        )
        return jsonify(deleted_connection), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def get_professor_annoucement():
    """Return professor announcements."""
    try:
        connection_controller = ProfessorController(current_app.config["Database"])
        annoucements = connection_controller.get_annoucement()
        return jsonify(annoucements), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def create_job_application(job_id: int) -> Optional[Dict]:
    """Create a job application in the database."""
    app_manager = JobApplicationController(current_app.config["Database"])
    return app_manager.create_job_application(job_id)


def fetch_user_job_applications() -> Optional[Dict]:
    """Fetch all job applications created by the current user."""
    app_manager = JobApplicationController(current_app.config["Database"])
    return app_manager.fetch_user_job_applications()


def fetch_job_applications_from_job(job_id: int) -> Optional[Dict]:
    """Fetch all job applications related to a job post by job ID."""
    app_manager = JobApplicationController(current_app.config["Database"])
    return app_manager.fetch_job_application_from_job_post(job_id)


def get_tag_by_id(tag_id: int):
    """Get a tag by its id."""
    try:
        skills = SkillsController(current_app.config["Database"])
        tag = skills.get_tag(tag_id)
        return jsonify(tag), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def get_term_by_id(term_id: int):
    """Get a term by its id."""
    try:
        skills = SkillsController(current_app.config["Database"])
        term = skills.get_term(term_id)
        return jsonify(term), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def get_all_terms():
    """Return all terms (id, name, type)."""
    try:
        skills = SkillsController(current_app.config["Database"])
        terms = skills.get_terms()
        return jsonify(terms), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def post_tag(body: Dict):
    """Create a tag or return existing tag id.

    Expects body: {"name": "tag name"}
    Returns: {"id": <tag_id>} with 201 if created, 200 if already existed.
    """
    try:
        if not body or "name" not in body:
            return jsonify({"message": "'name' is required"}), 400

        skills = SkillsController(current_app.config["Database"])
        name = body.get("name")
        try:
            tag_id, created = skills.post_tag(name)
        except ValueError as e:
            return jsonify({"message": str(e)}), 400
        except Exception:
            raise

        status = 201 if created else 200
        return jsonify({"id": tag_id}), status
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


def update_job_applications_status(job_id: int, body: list[Dict]) -> Optional[Dict]:
    """Update multiple job applications' status from the provided job."""
    app_manager = JobApplicationController(current_app.config["Database"])
    return app_manager.update_job_applications_status(job_id, body)


def get_file(file_id: str) -> Response:
    """Get a file for viewing, based on the file id."""
    file_manager = FileController(current_app.config["Database"])
    return file_manager.get_file(file_id)


def download_file(file_id: str) -> Response:
    """Get a file for downloading, based on the file id."""
    file_manager = FileController(current_app.config["Database"])
    return file_manager.download_file(file_id)
