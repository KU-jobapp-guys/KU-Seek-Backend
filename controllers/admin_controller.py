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
            .where(UserRequest.status != RequestStatusTypes.DENIED.value)
            .all()
        )
        records = [record.to_dict() for record in user_requests]
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
        pass

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
