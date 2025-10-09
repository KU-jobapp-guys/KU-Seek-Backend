"""Module for store api that relate to user profile."""

from typing import Optional, Dict
from connexion.exceptions import ProblemException
from .models.profile_model import Profile
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError


class ProfileController:
    """Controller to use CRUD operations for UserProfile."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    def get_profile_by_uid(self, user_id: str) -> Optional[Dict]:
        """
        Return a user profile in the database with the corresponding id.

        Retrieves a single user profile by user id from the MySQL database.

        Args:
            user_id: The unique ID of the user (string format).

        Returns:
            The user profile dictionary if found, otherwise None.
        """
        session = self.db.get_session()
        try:
            user_uuid = UUID(user_id)

            profile = (
                session.query(Profile)
                .filter(Profile.user_id == user_uuid)
                .one_or_none()
            )

            if not profile:
                raise ValueError(f"Profile for user_id={user_id} not found")

            return profile.to_dict()
        
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error fetching profile for user_id={user_id}: {e}")

        finally:
            session.close()

    def create_profile(self, user_id: str, body: Dict) -> Optional[Dict]:
        """
        Create new component in the UserProfile table.

        POST /users/profile
        """
        user_uuid = UUID(user_id)

        if not body:
            raise ProblemException(
                status=400,
                title="Invalid Request",
                detail="Request body cannot be empty.",
            )

        session = self.db.get_session()
        try:
            existing_profile = (
                session.query(Profile).where(Profile.user_id == user_uuid).one_or_none()
            )

            if existing_profile:
                raise ProblemException(
                    f"Profile already exists for user '{user_id}'",
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
            raise ProblemException(str(e))
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
                detail="Request body cannot be empty.",
            )

        session = self.db.get_session()
        try:
            profile = (
                session.query(Profile).where(Profile.user_id == user_uuid).one_or_none()
            )
            if not profile:
                raise ProblemException(
                    f"User profile with id '{user_id}' not found.",
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
            raise ProblemException(str(e))
        finally:
            session.close()

        return self.get_profile_by_uid(user_id)
