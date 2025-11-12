"""Module containing admin endpoints."""
from decorators import role_required


@role_required(["Admin"])
class AdminController:
    """Class for handling admin operations."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    def get_all_user_request(self):
        """
        Get all user creation requests.

        Get all the users which have been created, but not banned, with their
        user and profile data.

        returns: All non-resolved user creation records.
        """
        pass

    def update_user_status(self, body):
        """
        Update one or more user verification statuses.

        Update all user verification statuses from the request body.

        Args:
            body: The request body

        returns: A list of all updated user records.
        """
        pass

    def get_all_job_request(self):
        """
        Get all job post creation requests.

        Get all the job posts which have been created but not approved.

        returns: All non-resolved job post creation records.
        """
        pass

    def update_job_status(self, body):
        """
        Update one or more job post verification statuses.

        Update all job post verification statuses from the request body.

        Args:
            body: The request body

        returns: A list of all updated job post records.
        """
        pass