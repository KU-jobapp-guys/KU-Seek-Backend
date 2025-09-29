"""Module for store api that relate to user profile."""

from typing import Optional, Dict
from connexion.exceptions import ProblemException
from .db_controller import BaseController
from .models.profile_model import Profile
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError



class ProfileController(BaseController):
    """Controller to use CRUD operations for UserProfile."""

    def __init__(self):
        """Initialize the class."""
        super().__init__()
    

    def get_profile_by_uid(self, user_id: str) -> Optional[Dict]:
        """
        Return a user profile in the database with the corresponding id.

        Retrieves a single user profile by user id from the MySQL database.

        Args:
            user_id: The unique ID of the user (string format).

        Returns:
            The user profile dictionary if found, otherwise None.
        """
        session = self.get_session()
        try:
            user_uuid = UUID(user_id)

            profile = session.query(Profile).where(
                Profile.user_id == user_uuid
            ).one_or_none()
            if not profile:
                return None

            return profile.to_dict()

        except (ValueError, SQLAlchemyError) as e:
            print(f"Error fetching profile for user_id={user_id}: {e}")
            return None

        finally:
            session.close()
        

    def create_profile(self, user_id: str, body:Dict) -> Optional[Dict]:
        """
        Create new component in the UserProfile table.

        POST /users/profile
        """
        user_uuid = UUID(user_id)

        if not body:
            raise ProblemException(
                status=400,
                title="Invalid Request",
                detail="Request body cannot be empty."
            )
        

        session = self.get_session()
        try:
            existing_profile = session.query(Profile).where(
                Profile.user_id == user_uuid
            ).one_or_none()
            
            if existing_profile:
                raise ProblemException(
                    status=409,
                    title="Conflict",
                    detail=f"Profile already exists for user '{user_id}'"
                )
            
            profile = Profile()
            profile.user_id = user_uuid
            
            for key, value in body.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            session.add(profile)
            session.commit()

        except ProblemException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise ProblemException(
                status=500,
                title="Database Error",
                detail=str(e)
            )
        finally:
            session.close()

        return self.get_profile_by_uid(user_id)


    def update_profile(self, user_id: str, body: Dict) -> Optional[Dict]:
        """
        Update fields in the UserProfile table dynamically.

        PATCH /users/profile
        """
        user_uuid = UUID(user_id)

        if not body:
            raise ProblemException(
                status=400,
                title="Invalid Request",
                detail="Request body cannot be empty."
            )

        session = self.get_session()
        try:
            profile = session.query(Profile).where(
                Profile.user_id == user_uuid
            ).one_or_none()
            if not profile:
                raise ProblemException(
                    status=404,
                    title="Not Found",
                    detail=f"User profile with id '{user_id}' not found."
                )

            for key, value in body.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)

            session.commit()

        except ProblemException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise ProblemException(
                status=500,
                title="Database Error",
                detail=str(e)
            )
        finally:
            session.close()

        return self.get_profile_by_uid(user_id)
    