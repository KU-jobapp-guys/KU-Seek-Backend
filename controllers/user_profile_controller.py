"""Module for store api that relate to user profile."""

from typing import Optional, Dict
from connexion.exceptions import ProblemException
from .models.profile_model import Profile
from .models.user_model import User, UserTypes, Student, Company
from .education_controller import EducationController

from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError


class ProfileController:
    """Controller to use CRUD operations for UserProfile."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database
        self.education_controller = EducationController(database)

    def get_user_setting(self, user_id: str) -> Optional[Dict]:
        """
        Return a user setting in the database.

        Retrieves a user setting from the MySQL database.

        Returns:
            The user setting dictionary if found, otherwise None.
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
                print(f"Profile for user_id={user_id} not found")
                raise ValueError(f"Profile for user_id={user_id} not found")

            profile_obj = {
                "id": str(profile.user_id),
                "firstName": profile.first_name,
                "lastName": profile.last_name,
                "age": profile.age,
                "gender": profile.gender,
                "location": profile.location,
                "email": profile.email,
                "contactEmail": profile.contact_email,
                "phoneNumber": profile.phone_number,
            }

            if profile.user_type == "student":
                student = (
                    session.query(Student)
                    .filter(Student.user_id == user_uuid)
                    .one_or_none()
                )
                if student:
                    profile_obj["gpa"] = student.gpa

            elif profile.user_type == "company":
                company = (
                    session.query(Company)
                    .filter(Company.user_id == user_uuid)
                    .one_or_none()
                )
                if company:
                    profile_obj["name"] = company.company_name
            return profile_obj

        except SQLAlchemyError as e:
            print(f"Error fetching profile for user_id={user_id}: {e}")
            raise RuntimeError(f"Error fetching profile for user_id={user_id}: {e}")
        finally:
            session.close()

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
                print(f"Profile for user_id={user_id} not found")
                raise ValueError(f"Profile for user_id={user_id} not found")

            profile_obj = {
                "id": str(user_uuid),
                "firstName": profile.first_name,
                "lastName": profile.last_name,
                "about": profile.about,
                "gender": profile.gender,
                "age": profile.age,
                "location": profile.location,
            }

            if profile.user_type == "student":
                student = (
                    session.query(Student)
                    .filter(Student.user_id == user_uuid)
                    .one_or_none()
                )
                if student:
                    profile_obj["interests"] = student.interests
                    profile_obj["educations"] = (
                        self.education_controller.get_educations_by_user(
                            user_uuid, session=session
                        )
                        or []
                    )
                    
            elif profile.user_type == "company":
                company = (
                    session.query(Company)
                    .filter(Company.user_id == user_uuid)
                    .one_or_none()
                )
                if company:
                    profile_obj["name"] = company.company_name
            return profile_obj

        except SQLAlchemyError as e:
            print(f"Error fetching profile for user_id={user_id}: {e}")
            raise RuntimeError(f"Error fetching profile for user_id={user_id}: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise RuntimeError(f"Unexpected error: {e}")
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
                "Request body cannot be empty.",
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
            print("Request body cannot be empty.")
            raise ProblemException("Request body cannot be empty.")

        camel_map = {
            "firstName": "first_name",
            "lastName": "last_name",
            "phoneNumber": "phone_number",
            "contactEmail": "contact_email",
        }

        mapped_body = {}
        for k, v in (body or {}).items():
            mapped_body[camel_map.get(k, k)] = v

        session = self.db.get_session()
        try:
            user = session.query(User).where(User.id == user_uuid).one_or_none()

            if not user:
                raise ValueError(f"User for user_id={user_id} not found")

            models_to_update = [Profile]

            if user.type == UserTypes.STUDENT:
                models_to_update.append(Student)
            elif user.type == UserTypes.COMPANY:
                models_to_update.append(Company)

            # Update all relevant models
            for model_class in models_to_update:
                self._update_model_fields(
                    session=session,
                    model_class=model_class,
                    user_id=user_uuid,
                    data=mapped_body,
                )

            session.commit()

        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(f"{e}")
        finally:
            session.close()
        return self.get_profile_by_uid(user_id)

    def _update_model_fields(self, session, model_class, user_id: UUID, data: Dict):
        """
        Helper function to update fields on any model instance.
        """

        instance = (
            session.query(model_class)
            .where(model_class.user_id == user_id)
            .one_or_none()
        )

        if not instance:
            raise ValueError(f"{model_class.__name__} for user_id={user_id} not found")

        # Update only fields that exist on the model
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        return instance
