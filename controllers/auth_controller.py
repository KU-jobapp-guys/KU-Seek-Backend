"""Module for sending csrf-tokens."""

import os
import json
import random
from datetime import datetime, timedelta, UTC
from uuid import UUID
from typing import Dict, TypedDict

import jwt
from jwt import encode, decode
from flask import make_response, request, jsonify, current_app
from flask_wtf.csrf import generate_csrf
from connexion.exceptions import ProblemException
from werkzeug.utils import secure_filename
from decouple import config
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from swagger_server.openapi_server import models
from logger.custom_logger import get_logger

from .models.user_model import User, Student, Company, Professor
from .models.profile_model import Profile
from .models.token_model import Token
from .models.tos_model import TOSAgreement
from .models.file_model import File
from .models.admin_request_model import UserRequest

from .management.admin import AdminModel
from .management.email.email_sender import EmailSender, GmailEmailStrategy


SECRET_KEY = config("SECRET_KEY", default="good-key123")

ALGORITHM = "HS512"

BASE_FILE_PATH = config("BASE_FILE_PATH", default="content")

REFRESH_EXP_TIME = config("REFRESH_TOKEN_EXPIRY_MIN", default=30)
ACCESS_EXP_TIME = config("ACCESS_TOKEN_EXPIRY_MIN", default=5)

logger = get_logger()


def get_auth_user_id(request):
    """Get the authenticated user ID to verify the user's identity for the operation."""
    token = request.headers.get("access_token")
    if not token:
        raise ProblemException(status=401, title="Unauthorized", detail="Missing token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("uid")
    except jwt.ExpiredSignatureError:
        raise ProblemException(status=401, title="Unauthorized", detail="Token expired")
    except jwt.InvalidTokenError:
        raise ProblemException(status=401, title="Unauthorized", detail="Invalid token")


class UserCredentials(TypedDict):
    """Schema for user credentials."""

    google_uid: str
    email: str
    user_type: str
    user_id: str


def get_csrf_token():
    """
    Return a CSRF-token.

    Creates a CSRF-token using the flask-WTF library for form validation.

    Returns: A response object with a CSRF-token in the body and cookie.
    """
    token = generate_csrf()
    response = make_response(jsonify(csrf_token=token))
    # set the csrf_token as a cookie
    response.set_cookie("csrf_token", token, httponly=False)
    return response


def get_new_access_token():
    """Return a new access token for authorizaation."""
    refresh_token = request.cookies.get("refresh_token")
    auth_controller = AuthenticationController(
        current_app.config["Database"], current_app.config["Admin"]
    )
    return auth_controller.refresh_access_token(refresh_token)


def logout():
    """
    Logout a user, clearing JWT tokens, headers, and active sessions in the database.

    Logout a user from all devices and sessions. The user's refresh token is used
    as proof of authentication for determining which user is logged in.
    """
    refresh_token = request.cookies.get("refresh_token")
    auth_controller = AuthenticationController(
        current_app.config["Database"], current_app.config["Admin"]
    )
    return auth_controller.logout_user(refresh_token)


def handle_credential_login(body: Dict):
    """
    Handle user authentication with local credentials.

    Login a user using local credentials. This method fails if no such
    user exsists in the database.

    Args:
        body: The request body consisting of {"email":"", "password":""}

    Returns: A json containing the users unique UID, and auth tokens.
    """
    auth_controller = AuthenticationController(
        current_app.config["Database"], current_app.config["Admin"]
    )
    return auth_controller.credential_login(body["email"], body["password"])


def handle_oauth_authentication(body: dict):
    """
    Handle user authentication and return user credentials.

    Exchanges the Google authorization code using the Google Oauth2 API,
    then login the user if user credentials exist, otherwise create a new user
    and return user credentials.

    Args:
        body: The request body

    Returns: A json containing the users unique UID, and auth tokens.
    """
    client_secrets_file = config("CLIENT_SECRETS_FILE", default="client_secret.json")
    redirect_uri = config("REDIRECT_URI", default="http://localhost:5173/login")
    base_path = os.path.join(os.getcwd(), BASE_FILE_PATH)

    form = request.form
    # Create the OAuth flow
    try:
        flow = Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
            redirect_uri=redirect_uri,
        )
    except Exception as e:
        return models.ErrorMessage(
            f"Error during flow setup invalid flow credentails, {e}"
        ), 400

    # Exchange the authorization code for tokens
    try:
        flow.fetch_token(code=form.get("code"))
    except Exception as e:
        return models.ErrorMessage(f"Invalid authorization code, {e}"), 400

    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
        requests.Request(),
        audience=config("CLIENT_ID", default="very-secret-client-id"),
        clock_skew_in_seconds=10,
    )

    auth_controller = AuthenticationController(
        current_app.config["Database"], current_app.config["Admin"]
    )

    user = auth_controller.get_user("email", id_info["email"])
    if user:
        if not user.google_uid:
            auth_controller.add_user_google_uid(
                user_id=user.id, google_uid=id_info["sub"]
            )
        user_jwt, refresh, user_type, user_id = auth_controller.login_user(user.id)
    else:
        if not form.get("user_info"):
            return models.ErrorMessage("This account is not registered yet."), 400

        user_info = json.loads(form.get("user_info"))
        validation_file = request.files.get("id_doc")
        val_filename = secure_filename(validation_file.filename)
        val_filepath = base_path + "/" + val_filename
        validation_file.save(val_filepath)
        validation_res = json.loads(
            auth_controller.admin.verify_user(user_info, val_filepath)
        )
        user_info["google_uid"] = id_info["sub"]
        user_info["email"] = id_info["email"]
        user_info["user_type"] = (
            validation_res["role"] if validation_res["valid"] else "staff"
        )

        user_id = auth_controller.register_user(user_info, user_info["user_type"])
        user_jwt, refresh, user_type, user_id = auth_controller.login_user(user_id)

        post_register_process(
            user_id,
            user_info,
            validation_file,
            validation_res,
            user_type,
            id_info["email"],
        )

    response = make_response(
        models.UserCredentials(
            user_jwt, id_info["email"], user_type, user_id
        ).to_dict(),
        200,
    )
    response.set_cookie(
        "refresh_token", refresh, max_age=timedelta(days=30), httponly=True
    )
    return response


def handle_credential_authentication(body: dict):
    """
    Handle user authentication and return user credentials with email and password.

    Login the user if user email, otherwise create a new user
    and return user credentials.

    Args:
        body: The request body

    Returns: A json containing the users unique UID, and auth tokens.
    """
    form = request.form
    user_info = json.loads(form.get("user_info"))
    email = user_info.get("email")
    password = user_info.get("password")
    base_path = os.path.join(os.getcwd(), BASE_FILE_PATH)

    auth_controller = AuthenticationController(
        current_app.config["Database"], current_app.config["Admin"]
    )

    user = auth_controller.get_user("email", email)
    if user:
        if (user.password is None) or (request.files.get("id_doc") is not None):
            return models.ErrorMessage("This email has been registered."), 400
        return auth_controller.credential_login(email, password)
    else:
        validation_file = request.files.get("id_doc")
        val_filename = secure_filename(validation_file.filename)
        val_filepath = base_path + "/" + val_filename
        validation_file.save(val_filepath)
        validation_res = json.loads(
            auth_controller.admin.verify_user(user_info, val_filepath)
        )
        user_info["email"] = email
        user_info["user_type"] = (
            validation_res["role"] if validation_res["valid"] else "staff"
        )

        print("user_info: ", user_info)

        user_id = auth_controller.register_user(user_info, user_info["user_type"])
        user_jwt, refresh, user_type, user_id = auth_controller.login_user(user_id)

        post_register_process(
            user_id, user_info, validation_file, validation_res, user_type, email
        )

        response = make_response(
            models.UserCredentials(user_jwt, email, user_type, user_id).to_dict(), 200
        )
        response.set_cookie(
            "refresh_token", refresh, max_age=timedelta(days=30), httponly=True
        )
        return response


def post_register_process(
    user_id: str,
    user_info: dict,
    validation_file,
    validation_res: dict,
    user_type: str,
    email: str,
):
    """
    Perform post-registration tasks for a new user.

    This includes:

    - Saving the validation file.
    - Creating the user request.
    - Setting up the user profile.
    - Sending a welcome email.
    """
    session = current_app.config["Database"].get_session()

    # Save validation file
    file_name = secure_filename(validation_file.filename)
    validation_file_model = File(
        owner=UUID(user_id),
        file_name=file_name,
        file_path="temp",
        file_type="validation_file",
    )
    session.add(validation_file_model)
    session.flush()  # Get the ID

    # Create user request
    user_request = UserRequest(
        user_id=UUID(user_id),
        requested_type=user_info["user_type"],
        verification_document=validation_file_model.id,
        denial_reason=validation_res.get("reason"),
    )
    session.add(user_request)

    # Create profile
    profile = Profile(
        user_id=UUID(user_id),
        first_name=user_info.get("firstName", ""),
        last_name=user_info.get("lastName", ""),
        user_type=user_type,
        email=email,
        contact_email=email,
    )
    session.add(profile)

    session.commit()
    session.close()

    # Send welcome email
    if user_info["user_type"] == "student":
        mail_file = "welcome_student"
    elif user_info["user_type"] == "company":
        mail_file = "welcome_company"
    else:
        mail_file = "welcome"
    try:
        email_sender = EmailSender(GmailEmailStrategy())
        email_sender.send_email(
            email, "Welcome to KU-Seek", mail_file, template_args=[]
        )
    except Exception as e:
        logger.error("Registration email error: ", e)


class AuthenticationController:
    """Controller for fetching database authentication credentials."""

    def __init__(self, database, admin: AdminModel):
        """Init the class."""
        self.db = database
        self.admin = admin

    def check_users(self, field: str, value: str) -> bool:
        """Check if a user exists in the users table."""
        session = self.db.get_session()
        exists = (
            session.query(User).filter(getattr(User, field) == value).first()
            is not None
        )
        session.close()
        return exists

    def logout_user(self, refresh_token: str) -> bool:
        """
        Logout a user from the system.

        Logout the user with the provided refresh_token.
        This method returns nothing if the proof of authentication
        is invalid, or there are no active sessions in the database.

        Args:
            refresh_token: A JWT, containing the user's session

        returns A boolean denoting whether the logout is successful
        """
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            uid = payload.get("uid")
            refresh_id = payload.get("refresh_id")
        except jwt.ExpiredSignatureError:
            raise ProblemException(
                status=401, title="Unauthorized", detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise ProblemException(
                status=401, title="Unauthorized", detail="Invalid token"
            )

        try:
            session = self.db.get_session()
            # check if the refresh token exists
            session.query(Token).where(
                Token.uid == UUID(uid), Token.refresh_id == refresh_id
            ).one_or_none()
            if not refresh_token:
                session.close()
                raise ProblemException(
                    status=401, title="Unauthorized", detail="Invalid token"
                )

            session.query(Token).where(Token.uid == UUID(uid)).delete()
            session.commit()
            session.close()

            response = make_response({"Detail": "Successfully logged out."}, 200)

            # set the refresh token to expire immediately
            response.set_cookie("refresh_token", max_age=0, httponly=True)

            return response

        except Exception as e:
            session.rollback()
            session.close()
            raise ProblemException(
                status=500, title="Server Error", detail=f"Database Error occured: {e}"
            )

    def login_user(self, uid: str) -> Dict[str, str]:
        """
        Login a user into the system.

        Login the user with the provided user id,
        then return access and refresh tokens for proof of authentication.

        Args:
            uid: The user's user id in UUID4 format

        Returns: A tuple containing access and refresh tokens
        """
        # access token generation
        iat = int(datetime.now(UTC).timestamp())
        exp = int((datetime.now(UTC) + timedelta(hours=1)).timestamp())

        payload = {"uid": str(uid), "iat": iat, "exp": exp}

        auth_token = encode(payload, SECRET_KEY, algorithm="HS512")

        # Refresh token payload
        refresh_id = random.getrandbits(32)
        iat = int(datetime.now(UTC).timestamp())
        exp = int((datetime.now(UTC) + timedelta(hours=30)).timestamp())

        payload = {"uid": str(uid), "refresh": refresh_id, "iat": iat, "exp": exp}

        refresh_token = encode(payload, SECRET_KEY, algorithm="HS512")

        session = self.db.get_session()
        token = Token(uid=uid, refresh_id=refresh_id)
        session.add(token)
        session.commit()
        user = session.query(User).where(User.id == uid).one()
        user_type = user.type.value.lower()
        user_id = str(uid)
        session.close()

        current_app.config["RateLimiter"].unban_user(str(uid))
        return auth_token, refresh_token, user_type, user_id

    def get_user_id(self, field: str, value: str):
        """Return the user id with the matching field and value."""
        session = self.db.get_session()
        try:
            user = self.get_user(field, value)
            if not user:
                return None
            return user.id
        finally:
            session.close()

    def get_user(self, field: str, value: str):
        """Return the user with the matching field and value."""
        session = self.db.get_session()
        try:
            user = (
                session.query(User).where(getattr(User, field) == value).one_or_none()
            )
            return user
        finally:
            session.close()

    def add_user_google_uid(self, user_id: str, google_uid: str):
        """Link google_Uid for existing users."""
        session = self.db.get_session()

        user = session.query(User).filter_by(id=user_id).first()
        if user:
            if google_uid and not user.google_uid:
                user.google_uid = google_uid
                session.commit()
        session.close()

    def register_user(self, credentials: UserCredentials, user_type: str) -> str:
        """
        Register a new user using the provided credentials and type.

        Create a new credentials in the database based on the provided credentials.
        The user will have additional information filled out based on the user type.

        Args:
            credentials: The account's credentials
            user_type: The user's type {student, company, staff, professor}

        Returns: The user's id in the database
        """
        required_oauth_keys = ["google_uid", "email", "user_type"]
        required_credential_keys = ["email", "password", "user_type"]
        valid_keys = all(key in credentials for key in required_oauth_keys) or all(
            key in credentials for key in required_credential_keys
        )
        if not valid_keys:
            raise TypeError("Invalid credentials.")

        session = self.db.get_session()
        hasher = PasswordHasher()

        # register the user in the system
        user = User(
            google_uid=credentials.get("google_uid")
            if credentials.get("google_uid")
            else None,
            email=credentials["email"],
            type=credentials["user_type"],
            password=hasher.hash(credentials["password"])
            if credentials.get("password")
            else None,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id

        # role based tables
        if user_type == "student":
            student = Student(user_id=user_id, nisit_id=credentials["kuId"])
            session.add(student)
            session.commit()
        elif user_type == "professor":
            professor = Professor(user_id=user_id)
            session.add(professor)
            session.commit()
        elif user_type == "company":
            company = Company(
                user_id=user_id,
                company_name=credentials["companyName"],
                company_size=credentials["companySize"],
            )
            session.add(company)
            session.commit()

        tos = TOSAgreement(user_id=user_id, agree_status=True)
        session.add(tos)
        session.commit()

        session.close()

        return user_id

    def refresh_access_token(self, refresh_token: str):
        """
        Return a new access token for authorization.

        Validates the refresh token in the request header and
        returns a new access and refresh token pair for user authentication
        and authorization. The new refresh token is returned in the header.

        Returns: A new access token and refresh token cookie.
        """
        try:
            refresh_id = decode(jwt=refresh_token, key=SECRET_KEY, algorithms=["HS512"])
        except Exception as e:
            return models.ErrorMessage(f"Could not decode JWT, {e}"), 400

        session = self.db.get_session()
        valid_token = (
            session.query(Token).where(Token.refresh_id == refresh_id).one_or_none()
        )

        if not valid_token:
            return models.ErrorMessage("Invalid refresh token"), 400

        user_id = valid_token.uid
        session.close()

        access, refresh = self.login_user(user_id)

        response = make_response(access, 200)
        # set the refresh token as a HttpOnly cookie
        response.set_cookie(
            "refresh_token", refresh, max_age=timedelta(days=30), httponly=True
        )

        return response

    def credential_login(self, email: str, password: str):
        """Login the user using the provided email and password."""
        session = self.db.get_session()
        try:
            user = session.query(User).where(User.email == email).one_or_none()
        except Exception:
            session.close()
            return models.ErrorMessage("Database error occurred"), 400

        if not user:
            session.close()
            return models.ErrorMessage(
                "Could not find user with the provided email"
            ), 404

        session.close()
        try:
            ph = PasswordHasher()
            if ph.verify(user.password, password):
                user_jwt, refresh, user_type, _ = self.login_user(user.id)
                response = make_response(
                    models.UserCredentials(user_jwt, email, user_type).to_dict(), 200
                )
                # set the refresh token as a HttpOnly cookie
                response.set_cookie(
                    "refresh_token", refresh, max_age=timedelta(days=30), httponly=True
                )

                return response
        except VerifyMismatchError:
            return models.ErrorMessage("Password is invalid"), 403
