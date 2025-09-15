"""Module for store api that relate to user profile."""

from .db_controller import BaseController

class ProfileController(BaseController):
    """Controller to use CRUD operations for UserProfile."""

    def __init__(self):
        """Initialize the class."""
        super().__init__()
    

    def update_profile(self, user_id:str, body:dict) -> dict:
        """
        Update fields in the UserProfile table.

        Update user profile in the MySQL database.
        Corresponds to: PATCH /users/{user_id}/profile
        """
        return {}
    