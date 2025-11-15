"""Module containing admin endpoints."""

from flask import request
from jwt import decode
from .decorators import role_required
from .db_controller import AbstractDatabaseController
from .models.admin_request_model import UserRequest, JobRequest, RequestStatusTypes
from .models.job_model import Job
from .models.user_model import User, UserTypes, Company
from .models.profile_model import Profile
from swagger_server.openapi_server import models
from decouple import config
from datetime import datetime, timezone
from .serialization import camelize


SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class AdminController:
    """Class for handling admin operations."""

    def __init__(self, database):
        """Initialize the class."""
        self.db: AbstractDatabaseController = database

    def _format_user_request(
        self, user_request: UserRequest, name: str
    ) -> dict:
        """
        Format a user request with profile data into a dictionary.

        Args:
            user_request: The UserRequest object
            name: The name of the user or company

        Returns:
            Dictionary with user request and profile data
        """
        request_dict = user_request.to_dict()
        request_dict["name"] = name
        request_dict["requested_type"] = request_dict["requested_type"].value
        request_dict["status"] = request_dict["status"].value
        return camelize(request_dict)

    def _format_job_request_with_job(self, job_request: JobRequest, job: Job) -> dict:
        """
        Format a job request with job data into a dictionary.

        Args:
            job_request: The JobRequest object
            job: The Job object

        Returns:
            Dictionary with job request and job data
        """
        request_dict = job_request.to_dict()
        request_dict["job"] = job.to_dict()
        request_dict["status"] = request_dict["status"].value
        return camelize(request_dict)

    @role_required(["Admin"])
    def get_all_user_request(self):
        """
        Get all user creation requests.

        Get all the users which have been created, but not banned, with their
        user and profile data.

        returns: All non-resolved user creation records.
        """
        session = self.db.get_session()
        # query non-company users
        user_requests = (
            session.query(UserRequest, Profile.first_name, Profile.last_name)
            .join(Profile, Profile.user_id == UserRequest.user_id)
            .where(
                UserRequest.status != RequestStatusTypes.DENIED,
                UserRequest.requested_type != UserTypes.COMPANY,
            )
            .all()
        )

        # query company users
        company_requests = (
            session.query(UserRequest, Company.company_name)
            .join(Company, Company.user_id == UserRequest.user_id)
            .where(
                UserRequest.status != RequestStatusTypes.DENIED,
                UserRequest.requested_type == UserTypes.COMPANY,
            )
            .all()
        )

        records = [
            self._format_user_request(request, first_name + last_name)
            for request, first_name, last_name in user_requests
        ]

        company_records = [
            self._format_user_request(request, company_name)
            for request, company_name in company_requests
        ]

        records += company_records

        session.close()
        return records, 200

    @role_required(["Admin"])
    def update_user_status(self, body):
        """
        Update one or more user verification statuses.

        Update all user verification statuses from the request body.

        Args:
            body: The request body

        returns: A list of all updated user records.
        """
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])
        session = self.db.get_session()
        try:
            accept_ids = [
                item["user_id"]
                for item in body
                if item["is_accepted"] and not item.get("delete", False)
            ]
            # approve users
            records = (
                session.query(UserRequest, User)
                .join(User, User.id == UserRequest.user_id)
                .where(UserRequest.id.in_(accept_ids))
                .all()
            )
            for user_request, user in records:
                user_request.status = RequestStatusTypes.APPROVED
                user_request.approved_by = token_info["user_id"]
                user_request.approved_at = datetime.now(timezone.utc)
                user.type = user_request.requested_type
                user.is_verified = True
                session.add_all([user_request, user])

            # deny users
            deny_ids = [
                item["user_id"]
                for item in body
                if not item["is_accepted"] and not item.get("delete", False)
            ]
            records = (
                session.query(UserRequest).where(UserRequest.id.in_(deny_ids)).all()
            )
            for user_request in records:
                user_request.status = RequestStatusTypes.DENIED
                user_request.approved_at = datetime.now(timezone.utc)
                user_request.approved_by = token_info["user_id"]
                session.add(user_request)

            # delete users
            delete_ids = [item["user_id"] for item in body if item["delete"]]
            records = (
                session.query(UserRequest, User)
                .join(User, User.id == UserRequest.user_id)
                .where(UserRequest.id.in_(delete_ids))
                .all()
            )
            for user_request, user in records:
                session.delete(user)

            response = {
                "accepted": accept_ids,
                "denied": deny_ids,
                "deleted": delete_ids,
            }

            session.commit()
            session.close()
            return response, 200
        except Exception:
            session.rollback()
            session.close()
            return models.ErrorMessage("Could not update ids."), 400

    @role_required(["Admin"])
    def get_all_job_request(self):
        """
        Get all job post creation requests.

        Get all the job posts which have been created but not approved.

        returns: All non-resolved job post creation records.
        """
        session = self.db.get_session()
        job_requests = (
            session.query(JobRequest, Job, Company.company_name)
            .join(Job, Job.id == JobRequest.job_id)
            .join(Company, Company.id == Job.company_id)
            .where(JobRequest.status != RequestStatusTypes.DENIED)
            .all()
        )

        records = [
            self._format_job_request_with_job(request, job)
            for request, job in job_requests
        ]

        session.close()
        return records, 200

    @role_required(["Admin"])
    def update_job_status(self, body):
        """
        Update one or more job post verification statuses.

        Update all job post verification statuses from the request body.

        Args:
            body: The request body

        returns: A list of all updated job post records.
        """
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])
        session = self.db.get_session()
        try:
            accept_ids = [
                item["job_id"]
                for item in body
                if item["is_accepted"] and not item.get("delete", False)
            ]
            # approve jobs
            records = (
                session.query(JobRequest, Job)
                .join(Job, Job.id == JobRequest.job_id)
                .where(JobRequest.id.in_(accept_ids))
                .all()
            )
            for job_request, job in records:
                job_request.status = RequestStatusTypes.APPROVED
                job_request.approved_by = token_info["user_id"]
                job_request.approved_at = datetime.now(timezone.utc)
                job.status = "approved"
                job.visibiity = True
                job.approved_by = token_info["user_id"]
                session.add_all([job_request, job])

            # deny jobs
            deny_ids = [
                item["job_id"]
                for item in body
                if not item["is_accepted"] and not item.get("delete", False)
            ]
            records = (
                session.query(JobRequest, Job)
                .join(Job, Job.id == JobRequest.job_id)
                .where(JobRequest.id.in_(deny_ids))
                .all()
            )
            for job_request, job in records:
                job_request.status = RequestStatusTypes.DENIED
                job_request.approved_at = datetime.now(timezone.utc)
                job_request.approved_by = token_info["user_id"]
                job.status = "rejected"
                session.add_all([job_request, job])

            # delete jobs
            delete_ids = [item["job_id"] for item in body if item["delete"]]
            records = (
                session.query(JobRequest, Job)
                .join(Job, Job.id == JobRequest.job_id)
                .where(JobRequest.id.in_(delete_ids))
                .all()
            )
            for job_request, job in records:
                session.delete(job)

            response = {
                "accepted": accept_ids,
                "denied": deny_ids,
                "deleted": delete_ids,
            }

            session.commit()
            session.close()
            return response, 200
        except Exception:
            session.rollback()
            session.close()
            return models.ErrorMessage("Could not update ids."), 400
