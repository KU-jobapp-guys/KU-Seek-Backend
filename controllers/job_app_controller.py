"""Module containing endpoints for job applications."""

from uuid import UUID
from jwt import decode
from .decorators import role_required
from flask import request
from decouple import config
from sqlalchemy.orm import joinedload
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
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        session = self.db.get_session()

    @role_required(["Student"])
    def fetch_user_job_applications(self):
        """Fetch all job applications belonging to the owner."""
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        session = self.db.get_session()

        job_apps = (
            session.query(JobApplication)
            .options(joinedload(JobApplication.job))
            .where(JobApplication.user_id == UUID(token_info["uid"]))
            .all()
        )

        applications = [j_app.to_dict() for j_app in job_apps]
        detailed_apps = [j_app.job.to_dict() for j_app in applications]
        formatted_apps = [
            models.JobApplication(
                applicant={
                    "user_id": str(j_app.student_id),
                    "first_name": j_app.first_name,
                    "last_name": j_app.last_name,
                    "contact_email": j_app.contact_email,
                },
                job_details={
                    "job_id": str(j_app.job.id),
                    "job_title": j_app.job.title,
                },
                resume=j_app.resume,
                letter_of_application=j_app.letter_of_application,
                years_of_experience=j_app.years_of_experience,
                expected_salary=j_app.expected_salary,
                phone_number=j_app.phone_number,
                status=j_app.status,
                applied_at=j_app.applied_at,
            )
            for j_app in detailed_apps
        ]

        session.close()

        return formatted_apps, 200

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

        formatted_apps = [
            models.JobApplication(
                applicant={
                    "user_id": str(j_app.student_id),
                    "first_name": j_app.first_name,
                    "last_name": j_app.last_name,
                    "contact_email": j_app.contact_email,
                },
                resume=j_app.resume,
                letter_of_application=j_app.letter_of_application,
                years_of_experience=j_app.years_of_experience,
                expected_salary=j_app.expected_salary,
                phone_number=j_app.phone_number,
                status=j_app.status,
                applied_at=j_app.applied_at,
            )
            for j_app in applications
        ]

        session.close()

        return formatted_apps, 200
