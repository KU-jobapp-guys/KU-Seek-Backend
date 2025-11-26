"""Module for store api that relate to user profile."""

from typing import Optional, Dict
from swagger_server.openapi_server import models
from logger.custom_logger import get_logger
from .models.profile_model import Profile, ProfileSkills
from .models.user_model import User, UserTypes, Student, Company
from .decorators import login_required, rate_limit
from jwt import decode
from flask import request
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from decouple import config
import os
from werkzeug.utils import secure_filename
from .models.file_model import File
from .models.tag_term_model import Tags
from .serialization import decamelize

SECRET_KEY = config("SECRET_KEY", default="good-key123")

ALGORITHM = "HS512"

BASE_FILE_PATH = config("BASE_FILE_PATH", default="content")
SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")

logger = get_logger()


class ProfileController:
    """Controller to use CRUD operations for UserProfile."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    @login_required
    @rate_limit
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

    @login_required
    @rate_limit
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
            try:
                user_uuid = UUID(user_id)
            except (ValueError, TypeError):
                return (
                    models.ErrorMessage(f"Profile for user_id={user_id} not found"),
                    404,
                )

            profile = (
                session.query(Profile)
                .filter(Profile.user_id == user_uuid)
                .one_or_none()
            )

            if not profile:
                logger.warning("Profile for user_id=%s not found", user_id)
                return models.ErrorMessage(
                    f"Profile for user_id={user_id} not found"
                ), 404

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
                "profileImg": profile.profile_img,
                "profileBanner": profile.banner_img,
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
                    profile_obj["industry"] = company.company_industry
                    profile_obj["size"] = company.company_size
                    profile_obj["fullLocation"] = company.full_location
                    profile_obj["companyType"] = company.company_type
                    profile_obj["companyWebsite"] = company.company_website
                    profile_obj["profilePhoto"] = profile.profile_img
                    profile_obj["bannerPhoto"] = profile.banner_img

            skills = (
                session.query(Tags.name)
                .join(ProfileSkills, ProfileSkills.skill_id == Tags.id)
                .filter(ProfileSkills.user_id == user_uuid)
                .all()
            )
            profile_obj["workFields"] = [s[0] for s in skills] if skills else []

            return profile_obj

        except SQLAlchemyError:
            logger.exception("Database error fetching profile for user_id=%s", user_id)
            return models.ErrorMessage("Database error fetching profile"), 500
        finally:
            session.close()

    @rate_limit
    def create_profile(self, user_id: str, body: Dict) -> Optional[Dict]:
        """
        Create new component in the UserProfile table.

        POST /users/profile
        """
        user_uuid = UUID(user_id)

        if not body:
            return models.ErrorMessage("Request body cannot be empty."), 400

        session = self.db.get_session()
        try:
            existing_profile = (
                session.query(Profile).where(Profile.user_id == user_uuid).one_or_none()
            )

            if existing_profile:
                logger.warning("Profile already exists for user %s", user_id)
                return models.ErrorMessage(
                    f"Profile already exists for user '{user_id}'",
                ), 409

            profile = Profile()
            profile.user_id = user_uuid

            for key, value in body.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)

            session.add(profile)
            session.commit()

        except Exception:
            session.rollback()
            logger.exception("Failed to create profile for user_id=%s", user_id)
            session.close()
            return models.ErrorMessage("Failed to create profile"), 500
        finally:
            session.close()

        return self.get_profile_by_uid(user_id)

    @login_required
    @rate_limit
    def update_profile(self, user_id: str, body: Dict) -> Optional[Dict]:
        """
        Update fields in the UserProfile table dynamically.

        Corresponds to PATCH /users/profile
        """
        user_uuid = UUID(user_id)
        if not body:
            logger.warning("Empty request body for update_profile user_id=%s", user_id)
            return models.ErrorMessage("Request body cannot be empty."), 400

        decamel = decamelize(body or {})

        mapped_body = dict(decamel)

        if "name" in mapped_body and "company_name" not in mapped_body:
            mapped_body["company_name"] = mapped_body.pop("name")

        if "companyType" in mapped_body and "company_type" not in mapped_body:
            mapped_body["company_type"] = mapped_body.pop("companyType")

        if "companyWebsite" in mapped_body and "company_website" not in mapped_body:
            mapped_body["company_website"] = mapped_body.pop("companyWebsite")

        if "industry" in mapped_body and "company_industry" not in mapped_body:
            mapped_body["company_industry"] = mapped_body.pop("industry")

        if "size" in mapped_body and "company_size" not in mapped_body:
            mapped_body["company_size"] = mapped_body.pop("size")

        session = self.db.get_session()
        try:
            user = session.query(User).where(User.id == user_uuid).one_or_none()

            if not user:
                logger.warning("User for user_id=%s not found", user_id)
                session.close()
                return models.ErrorMessage(f"User for user_id={user_id} not found"), 404

            models_to_update = [Profile]

            if user.type == UserTypes.STUDENT:
                models_to_update.append(Student)
            elif user.type == UserTypes.COMPANY:
                models_to_update.append(Company)

            work_fields = mapped_body.pop("work_fields", None)
            if work_fields is not None:
                if not isinstance(work_fields, (list, tuple)):
                    logger.warning("Invalid workFields type for user_id=%s", user_id)
                    session.close()
                    return models.ErrorMessage("workFields must be a list"), 400

                session.query(ProfileSkills).filter(
                    ProfileSkills.user_id == user_uuid
                ).delete(synchronize_session=False)

                for tag_name in work_fields:
                    if not tag_name:
                        continue
                    tag = session.query(Tags).where(Tags.name == tag_name).one_or_none()
                    if not tag:
                        tag = Tags(name=tag_name)
                        session.add(tag)
                        session.flush()

                    ps = ProfileSkills(user_id=user_uuid, skill_id=tag.id)
                    session.add(ps)

            for key in ("profile_img", "banner_img"):
                if key in mapped_body and not mapped_body[key]:
                    mapped_body.pop(key, None)

            for model_class in models_to_update:
                self._update_model_fields(
                    session=session,
                    model_class=model_class,
                    user_id=user_uuid,
                    data=mapped_body,
                )

            session.commit()

        except SQLAlchemyError:
            session.rollback()
            logger.exception("Database error updating profile for user_id=%s", user_id)
            session.close()
            return models.ErrorMessage("Database error updating profile"), 500
        finally:
            session.close()
        return self.get_profile_by_uid(user_id)

    @login_required
    @rate_limit
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
            return models.ErrorMessage("No image files provided"), 400

        session = self.db.get_session()
        saved_files = []

        try:
            profile = (
                session.query(Profile).where(Profile.user_id == user_uuid).one_or_none()
            )

            if not profile:
                profile = Profile(user_id=user_uuid)
                session.add(profile)
                session.flush()

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
                        full_previous_path = os.path.join(os.getcwd(), previous_file)
                        if os.path.exists(full_previous_path):
                            os.remove(full_previous_path)
                        profile_img.save(full_file_path)
                    except IOError:
                        raise IOError("Could not read/write files")
                    profile_file_model = existing_profile_img
                    saved_files.append(
                        {
                            "file_type": "profile_image",
                            "file_id": profile_file_model.id,
                            "file_path": existing_profile_img.file_path,
                            "full_path": full_file_path,
                        }
                    )
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
                    profile_file_model = profile_img_model
                    saved_files.append(
                        {
                            "file_type": "profile_image",
                            "file_id": profile_file_model.id,
                            "file_path": profile_img_model.file_path,
                            "full_path": full_file_path,
                        }
                    )

                print("PEAAA: ", profile_file_model.id)
                print("IS THERE PROFILE ", profile)
                print("IMG????: ", profile.profile_img)
                profile.profile_img = str(profile_file_model.id)
                print("IMG SHOULDN'T BLANK: ", profile.profile_img)

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
                        full_previous_path = os.path.join(os.getcwd(), previous_file)
                        if os.path.exists(full_previous_path):
                            os.remove(full_previous_path)
                        banner_img.save(full_file_path)
                    except IOError:
                        raise IOError("Could not save/write file.")
                    banner_file_model = existing_banner_img
                    saved_files.append(
                        {
                            "file_type": "banner_image",
                            "file_id": banner_file_model.id,
                            "file_path": existing_banner_img.file_path,
                            "full_path": full_file_path,
                        }
                    )
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
                    banner_file_model = banner_img_model
                    saved_files.append(
                        {
                            "file_type": "banner_image",
                            "file_id": banner_file_model.id,
                            "file_path": banner_img_model.file_path,
                            "full_path": full_file_path,
                        }
                    )
                profile.banner_img = str(banner_file_model.id)

            session.commit()
            session.close()

            response = [
                {
                    "file": entry["file_type"],
                    "status": "ok",
                    "file_id": str(entry.get("file_id")),
                    "file_path": entry.get("file_path"),
                }
                for entry in saved_files
            ]
            return response, 200

        except Exception:
            # Rollback database transaction
            session.rollback()
            session.close()

            # Cleanup saved files on error
            for entry in saved_files:
                fp = entry.get("full_path")
                if fp and os.path.exists(fp):
                    os.remove(fp)

            logger.exception("Failed to upload profile images for user_id=%s", user_id)
            return models.ErrorMessage("Failed to upload images"), 500

    def _update_model_fields(self, session, model_class, user_id: UUID, data: Dict):
        """Update fields on any model instance."""
        instance = (
            session.query(model_class)
            .where(model_class.user_id == user_id)
            .one_or_none()
        )

        if not instance:
            raise ValueError(f"{model_class.__name__} for user_id={user_id} not found")

        forbidden_keys = {"id", "user_id"}
        for key, value in data.items():
            if key in forbidden_keys:
                continue
            if hasattr(instance, key):
                setattr(instance, key, value)

        return instance
