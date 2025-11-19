"""Module for store api that relate to user profile."""

from typing import Optional, Dict
from connexion.exceptions import ProblemException
from .models.profile_model import Profile
from .models.user_model import User, UserTypes, Student, Company
from .decorators import login_required
from jwt import decode
from flask import request
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from decouple import config
import os
from werkzeug.utils import secure_filename
from .models.file_model import File
from .file_controller import FileController
from flask import current_app

SECRET_KEY = config("SECRET_KEY", default="good-key123")

ALGORITHM = "HS512"

BASE_FILE_PATH = config("BASE_FILE_PATH", default="content")
SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class ProfileController:
    """Controller to use CRUD operations for UserProfile."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    def get_user_setting(self, user_id: str) -> Optional[Dict]:
        """
        Return the currently logged in user.

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
            
            file_manager = FileController(current_app.config["Database"])

            profile_obj = {
                "id": str(profile.user_id),
                "firstName": profile.first_name,
                "lastName": profile.last_name,
                "about": profile.about,
                "age": profile.age,
                "gender": profile.gender,
                "location": profile.location,
                "email": profile.email,
                "contactEmail": profile.contact_email,
                "phoneNumber": profile.phone_number,
                "userType": profile.user_type,
                "isVerified": profile.is_verified,
                "profilePhoto": file_manager.get_file_as_blob(profile.profile_img) if profile.profile_img else '',
                "bannerPhoto": file_manager.get_file_as_blob(profile.banner_img) if profile.banner_img else '',
            }

            if profile.user_type == "student":
                student = (
                    session.query(Student)
                    .filter(Student.user_id == user_uuid)
                    .one_or_none()
                )
                if student:
                    profile_obj["interests"] = student.interests

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

    @login_required
    def update_profile(self, user_id: str, body: Dict) -> Optional[Dict]:
        """
        Update fields in the UserProfile table dynamically.

        Corresponds to PATCH /users/profile
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

    @login_required
    def upload_profile_images(self):
        """
        Upload new image files for the profile.

        Handle uploading of user profile and banner images.
        """
        jwt_auth_token = request.headers.get("access_token")
        user_id = decode(jwt_auth_token, SECRET_KEY, algorithms=[ALGORITHM])["uid"]
        user_uuid = UUID(user_id)

        files = request.files
        profile_img = files.get("profile_img")
        banner_img = files.get("banner_img")

        if not profile_img and not banner_img:
            raise ProblemException("No image files provided")

        session = self.db.get_session()
        saved_files = []

        try:
            profile = session.query(Profile).filter(Profile.user_id == user_uuid).one_or_none()
            if not profile:
                raise ProblemException(f"Profile for user_id={user_id} not found")

            # Helper function to handle saving/updating a file
            def save_file(file_obj, file_type_attr, type_name):
                existing_file = (
                    session.query(File)
                    .filter(File.owner == user_uuid, File.file_type == type_name)
                    .one_or_none()
                )
                file_name = secure_filename(file_obj.filename)
                file_extension = os.path.splitext(file_name)[1]

                if existing_file:
                    # Remove old file
                    previous_file_path = os.path.join(os.getcwd(), existing_file.file_path)
                    try:
                        os.remove(previous_file_path)
                    except FileNotFoundError:
                        print(f"Previous file {existing_file.file_path} not found, skipping remove")
                    except OSError as e:
                        raise IOError(f"Failed to remove previous file: {e}")

                    # Save new file
                    file_path = f"{BASE_FILE_PATH}/{existing_file.id}{file_extension}"
                    full_file_path = os.path.join(os.getcwd(), file_path)
                    file_obj.save(full_file_path)

                    # Update record
                    existing_file.file_name = file_name
                    existing_file.file_path = file_path
                    setattr(profile, file_type_attr, existing_file.id)
                    saved_files.append((full_file_path, type_name))
                else:
                    # Create new file record
                    new_file = File(
                        owner=user_uuid,
                        file_name=file_name,
                        file_path="temp",
                        file_type=type_name,
                    )
                    session.add(new_file)
                    session.flush()  # Get ID

                    # Save file
                    file_path = f"{BASE_FILE_PATH}/{new_file.id}{file_extension}"
                    full_file_path = os.path.join(os.getcwd(), file_path)
                    file_obj.save(full_file_path)
                    new_file.file_path = file_path

                    # Update profile
                    setattr(profile, file_type_attr, new_file.id)
                    saved_files.append((full_file_path, type_name))

            # Handle profile image
            if profile_img:
                save_file(profile_img, "profile_img", "profile_image")

            # Handle banner image
            if banner_img:
                save_file(banner_img, "banner_img", "banner_image")

            session.commit()
            response = [{"file": file[1], "status": "ok"} for file in saved_files]
            return response, 200

        except Exception as e:
            session.rollback()

            # Cleanup saved files on error
            for file_path, _ in saved_files:
                if os.path.exists(file_path):
                    os.remove(file_path)

            raise ProblemException(f"Failed to upload images: {str(e)}")
        finally:
            session.close()


    def _update_model_fields(self, session, model_class, user_id: UUID, data: Dict):
        """Update fields on any model instance."""
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
