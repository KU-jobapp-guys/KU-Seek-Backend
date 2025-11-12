"""Module containing admin endpoints."""

from .decorators import role_required
from db_controller import AbstractDatabaseController
from .models.admin_request_model import UserRequest, JobRequest, RequestStatusTypes
from .models.job_model import Job
from .models.profile_model import Profile


class AdminController:
    """Class for handling admin operations."""

    def __init__(self, database):
        """Initialize the class."""
        self.db: AbstractDatabaseController = database

    def _format_user_request_with_profile(self, user_request: UserRequest, first_name: str, last_name: str) -> dict:
        """
        Format a user request with profile data into a dictionary.
        
        Args:
            user_request: The UserRequest object
            first_name: First name from profile
            last_name: Last name from profile
            
        Returns:
            Dictionary with user request and profile data
        """
        request_dict = user_request.to_dict()
        request_dict['first_name'] = first_name
        request_dict['last_name'] = last_name
        return request_dict

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
        request_dict['job'] = job.to_dict()
        return request_dict

    @role_required(["Admin"])
    def get_all_user_request(self):
        """
        Get all user creation requests.

        Get all the users which have been created, but not banned, with their
        user and profile data.

        returns: All non-resolved user creation records.
        """
        session = self.db.get_session()
        user_requests = (
            session.query(UserRequest, Profile.first_name, Profile.last_name)
            .join(Profile, Profile.user_id == UserRequest.user_id)
            .where(UserRequest.status != RequestStatusTypes.DENIED)
            .all()
        )
        
        records = [
            self._format_user_request_with_profile(request, first_name, last_name)
            for request, first_name, last_name in user_requests
        ]
        
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
        pass

    @role_required(["Admin"])
    def get_all_job_request(self):
        """
        Get all job post creation requests.

        Get all the job posts which have been created but not approved.

        returns: All non-resolved job post creation records.
        """
        session = self.db.get_session()
        job_requests = (
            session.query(JobRequest, Job)
            .join(Job, Job.id == JobRequest.job_id)
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
        pass

