"""Module containing endpoints for job applications."""

from uuid import UUID
from jwt import decode
from decorators import role_required
from flask import request
from decouple import config
from models import User, Job, JobApplication
from swagger_server.openapi_server import models


SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class JobApplicationController:
    """Controller for handling job application operations."""

    def __init__(self, database):
        """Init the class."""
        self.db = database

    @role_required(["Student"])
    def create_job_application(self):
        """Create a new job application from the request body."""

    @role_required(["Student"])
    def fetch_user_job_applications(self):
        """Fetch all job applications belonging to the owner."""

    @role_required(["Company"])
    def fetch_job_application_from_job_post(self, job_id):
        """Fetch all job applications for a specific job post."""
