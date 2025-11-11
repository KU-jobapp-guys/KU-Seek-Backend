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

SECRET_KEY = config("SECRET_KEY", default="good-key123")

ALGORITHM = "HS512"

BASE_FILE_PATH = config("BASE_FILE_PATH", default="content")
SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class ProfileController:
    """Controller to use CRUD operations for UserProfile."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    @login_required
    def get_self_profile(self) -> Optional[Dict]:
        """
        Return the currently logged in user.

        Retrieves the profile of the currently logged in user.
        This method calls the more general get_profile_by_uid to optain the
        user's profile.

        Returns: The user profile dictonary if found, otherwise None.
        """
        jwt_auth_token = request.headers.get("access_token")
        user_id = decode(jwt_auth_token, SECRET_KEY, algorithms=[ALGORITHM])["uid"]
        user_id = user_id.replace("'", "")
        return self.get_profile_by_uid(user_id)

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
        PATCH /users/profile
        """
        user_uuid = UUID(user_id)
        if not body:
            print("Request body cannot be empty.")
            raise ProblemException("Request body cannot be empty.")

        print(body)
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
            # Handle profile image
            if profile_img:
                # Check if profile image already exists
                existing_profile_img = (
                    session.query(File)
                    .filter(File.owner == user_uuid, File.file_type == "profile_image")
                    .one_or_none()
                )

                if existing_profile_img:
                    # Update existing record
                    previous_file = existing_profile_img.file_path
                    file_name = secure_filename(profile_img.filename)
                    file_extension = os.path.splitext(file_name)[1]
                    file_path = (
                        f"{BASE_FILE_PATH}/{existing_profile_img.id}{file_extension}"
                    )
                    full_file_path = os.path.join(os.getcwd(), file_path)

                    existing_profile_img.file_name = file_name
                    existing_profile_img.file_path = file_path

                    try:
                        os.remove(os.getcwd(), previous_file)
                        profile_img.save(full_file_path)
                    except IOError:
                        raise IOError("Could not read/write files")
                    saved_files.append((full_file_path, "profile image"))
                else:
                    # Create new file record
                    file_name = secure_filename(profile_img.filename)
                    profile_img_model = File(
                        owner=user_uuid,
                        file_name=file_name,
                        file_path="temp",
                        file_type="profile_image",
                    )
                    session.add(profile_img_model)
                    session.flush()  # Get the ID

                    # Save file with ID in name
                    file_extension = os.path.splitext(file_name)[1]
                    file_path = (
                        f"{BASE_FILE_PATH}/{profile_img_model.id}{file_extension}"
                    )
                    full_file_path = os.path.join(os.getcwd(), file_path)
                    profile_img_model.file_path = file_path

                    profile_img.save(full_file_path)
                    saved_files.append((full_file_path, "profile image"))

            # Handle banner image
            if banner_img:
                # Check if banner image already exists
                existing_banner_img = (
                    session.query(File)
                    .filter(File.owner == user_uuid, File.file_type == "banner_image")
                    .one_or_none()
                )

                if existing_banner_img:
                    # Update existing record
                    previous_file = existing_banner_img.file_path
                    file_name = secure_filename(banner_img.filename)
                    file_extension = os.path.splitext(file_name)[1]
                    file_path = (
                        f"{BASE_FILE_PATH}/{existing_banner_img.id}{file_extension}"
                    )
                    full_file_path = os.path.join(os.getcwd(), file_path)

                    existing_banner_img.file_name = file_name
                    existing_banner_img.file_path = file_path

                    try:
                        os.remove(os.getcwd(), previous_file)
                        banner_img.save(full_file_path)
                    except IOError:
                        raise IOError("Could not save/write file.")
                    saved_files.append((full_file_path, "banner image"))
                else:
                    # Create new file record
                    file_name = secure_filename(banner_img.filename)
                    banner_img_model = File(
                        owner=user_uuid,
                        file_name=file_name,
                        file_path="temp",
                        file_type="banner_image",
                    )
                    session.add(banner_img_model)
                    session.flush()  # Get the ID

                    # Save file with ID in name
                    file_extension = os.path.splitext(file_name)[1]
                    file_path = (
                        f"{BASE_FILE_PATH}/{banner_img_model.id}{file_extension}"
                    )
                    full_file_path = os.path.join(os.getcwd(), file_path)
                    banner_img_model.file_path = file_path

                    banner_img.save(full_file_path)
                    saved_files.append((full_file_path, "banner image"))

            session.commit()
            session.close()

            response = [{"file": file[1], "status": "ok"} for file in saved_files]
            return response, 200

        except Exception as e:
            # Rollback database transaction
            session.rollback()
            session.close()

            # Cleanup saved files on error
            for file_path in saved_files:
                if os.path.exists(file_path[0]):
                    os.remove(file_path[0])

            raise ProblemException(f"Failed to upload images: {str(e)}")

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
