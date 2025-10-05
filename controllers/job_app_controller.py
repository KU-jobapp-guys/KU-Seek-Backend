"""Module containing endpoints for job applications."""

from uuid import UUID
from jwt import decode
from .decorators import role_required
from flask import request
from decouple import config
from .models import User, Job, JobApplication
from swagger_server.openapi_server import models


SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class JobApplicationController:
    """Controller for handling job application operations."""

    def __init__(self, database):
        """Init the class."""
        self.db = database

    @role_required(["Student"])
    def create_job_application(self, body, job_id):
        """Create a new job application from the request body."""

    @role_required(["Student"])
    def fetch_user_job_applications(self):
        """Fetch all job applications belonging to the owner."""
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        session = self.db.get_session()

        job_apps = (
            session.query(JobApplication)
            .where(JobApplication.user_id == UUID(token_info["uid"]))
            .all()
        )

        applications = [j_app.to_dict() for j_app in job_apps]

        return applications, 200

    @role_required(["Company"])
    def fetch_job_application_from_job_post(self, job_id):
        """Fetch all job applications for a specific job post."""
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        session = self.db.get_session()

        user = (
            session.query(User).where(User.id == UUID(token_info["uid"])).one_or_none()
        )

        job = session.query(Job).where(Job.id == job_id).one_or_none()

        if not job:
            return models.ErrorMessage("Invalid job provided"), 400

        if job.user_id != user.id:
            return models.ErrorMessage("User is not the job owner"), 403

        job_apps = (
            session.query(JobApplication).where(JobApplication.job_id == job_id).all()
        )

        applications = [j_app.to_dict() for j_app in job_apps]

        return applications, 200