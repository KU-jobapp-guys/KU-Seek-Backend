"""Module for sending csrf-tokens."""

import random
import jwt
import json
import os

from flask import make_response, request
from connexion.exceptions import ProblemException
from typing import Dict, TypedDict
from flask import jsonify, current_app
from flask_wtf.csrf import generate_csrf
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from decouple import config
from jwt import encode, decode
from swagger_server.openapi_server import models
from datetime import datetime, timedelta, UTC
from .models.user_model import User, Student, Company, Professor
from .models.token_model import Token
from .management.admin import AdminModel
from .management.email import EmailSender
from uuid import UUID
from werkzeug.utils import secure_filename


SECRET_KEY = config("SECRET_KEY", default="good-key123")

ALGORITHM = "HS512"

BASE_FILE_PATH = config("BASE_FILE_PATH", default="content")


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
    auth_controller = AuthenticationController(current_app.config["Database"], current_app.config["Admin"])
    return auth_controller.refresh_access_token(refresh_token)


def logout():
    """
    Logout a user, clearing JWT tokens, headers, and active sessions in the database.

    Logout a user from all devices and sessions. The user's refresh token is used
    as proof of authentication for determining which user is logged in.
    """
    refresh_token = request.cookies.get("refresh_token")
    auth_controller = AuthenticationController(current_app.config["Database"], current_app.config["Admin"])
    return auth_controller.logout_user(refresh_token)


def handle_authentication(body: Dict):
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

    # Decode JWT using Google ID Token helper
    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
        requests.Request(),
        audience=config("CLIENT_ID", default="very-secret-client-id"),
        clock_skew_in_seconds=10,
    )

    auth_controller = AuthenticationController(
        current_app.config["Database"], current_app.config["Admin"]
    )

    try:
        is_registered = auth_controller.check_users(id_info["sub"])
    except Exception as e:
        return models.ErrorMessage(f"Database error occured, {e}"), 400

    user_jwt = {}
    try:
        if is_registered:
            user = auth_controller.get_user(id_info["sub"])
            if user is None:
                raise ValueError("User was not found")
            user_jwt, refresh, user_type = auth_controller.login_user(user)

        else:
            user_info = form.get("user_info")
            user_info = json.loads(user_info)
            print(user_info)

            # process the file for validation
            validation_file = request.files.get("id_doc")
            print(validation_file.filename)
            val_filename = secure_filename(validation_file.filename)
            val_filepath = base_path + "/" + val_filename
            validation_file.save(val_filepath)

            validation_res = auth_controller.admin.verify_user(user_info, val_filepath)
            validation_res = json.loads(validation_res)
            print("AI result:", validation_res)
            if not validation_res["valid"]:
                raise ValueError("User did not pass validation")

            # reformat info like UserCredentails class
            user_info["email"] = id_info["email"]
            user_info["google_uid"] = id_info["sub"]
            user_info["user_type"] = validation_res["role"]
            user = auth_controller.register_user(user_info, validation_res["role"])
            user_jwt, refresh, user_type = auth_controller.login_user(user)

            # send a registration email
            if user_info["user_type"] == "student":
                mail_file = "welcome_student"
            elif user_info["user_type"] == "company":
                mail_file = "welcome_company"
            else:
                mail_file = "welcome"
            try:
                email = EmailSender()
                email.send_email(id_info["email"], "Welcome to KU-Seek", mail_file)
            except Exception:
                # implement logging later
                pass

        response = make_response(
            models.UserCredentials(user_jwt, id_info["email"], user_type).to_dict(), 200
        )
        # set the refresh token as a HttpOnly cookie
        response.set_cookie(
            "refresh_token", refresh, max_age=timedelta(days=30), httponly=True
        )

        return response
    except Exception as e:
        print(e)
        return models.ErrorMessage(
            f"Database error occured during authentication, {e}"
        ), 400


class AuthenticationController:
    """Controller for fetching database authentication credentials."""

    def __init__(self, database, admin: AdminModel):
        """Init the class."""
        self.db = database
        self.admin = admin

    def check_users(self, google_id: str):
        """Check if the user is in the users table."""
        session = self.db.get_session()
        users = session.query(User).all()

        if google_id in [user.google_uid for user in users]:
            session.close()
            return True

        session.close()
        return False

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

            response = make_response(
            {"Detail": "Successfully logged out."}, 200
            )

            # set the refresh token to expire immediately
            response.set_cookie(
                "refresh_token", max_age=0, httponly=True
            )

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
        exp = int((datetime.now(UTC) + timedelta(days=30)).timestamp())

        payload = {"uid": str(uid), "refresh": refresh_id, "iat": iat, "exp": exp}

        refresh_token = encode(payload, SECRET_KEY, algorithm="HS512")

        session = self.db.get_session()
        token = Token(uid=uid, refresh_id=refresh_id)
        session.add(token)
        session.commit()
        user = session.query(User).where(User.id == uid).one()
        user_type = user.type.value.lower()
        session.close()

        return auth_token, refresh_token, user_type

    def get_user(self, google_uid):
        """Return the user id with the matching google_uid."""
        session = self.db.get_session()
        user = session.query(User).where(User.google_uid == google_uid).one_or_none()
        if not user:
            session.close()
            return
        uid = user.id
        session.close()
        return uid

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
        keys = list(UserCredentials.__annotations__.keys())
        valid_keys = all(key in credentials for key in keys)
        if not valid_keys:
            raise TypeError("Invalid credentials.")

        session = self.db.get_session()

        # register the user in the system
        user = User(
            google_uid=credentials["google_uid"],
            email=credentials["email"],
            type=credentials["user_type"],
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
