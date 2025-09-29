"""Module for sending csrf-tokens."""

import random
from flask import make_response, request
from typing import Dict, TypedDict
from flask import jsonify
from flask_wtf.csrf import generate_csrf
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from decouple import config
from .db_controller import BaseController
from jwt import encode, decode
from swagger_server.openapi_server import models
from datetime import datetime, timedelta, UTC
from .models.user_model import User
from .models.token_model import Token


SECRET_KEY = config("SECRET_KEY", default="good-key123")


class UserCredentials(TypedDict):
    """Schema for user credentials."""

    username: str
    password: str
    user_type: str


def get_csrf_token():
    """
    Return a CSRF-token.

    Creates a CSRF-token using the flask-WTF library for form validation.

    Returns: A JSON with the csrf-token field.
    """
    return jsonify(csrf_token=generate_csrf())


def get_new_access_token():
    """Return a new access token for authorizaation."""
    refresh_token = request.cookies.get("refresh_token")
    auth_controller = AuthenticationController()
    return auth_controller.refresh_access_token(refresh_token)


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
        flow.fetch_token(code=body["code"])
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

    auth_controller = AuthenticationController()

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
            user_jwt, refresh = auth_controller.login_user(user)
        else:
            # hardcoding to company for now, since KU auth is not created
            user = auth_controller.register_user(
                {
                    "username": id_info["email"],
                    "password": id_info["at_hash"],
                    "user_type": "company",
                },
                id_info,
            )
            user_jwt, refresh = auth_controller.login_user(user)

        response = make_response(
            models.UserCredentials(user_jwt, id_info["email"]).to_dict(), 200
        )
        # set the refresh token as a HttpOnly cookie
        response.set_cookie(
            "refresh_token", refresh, max_age=timedelta(days=30), httponly=True
        )

        return response
    except Exception as e:
        return models.ErrorMessage(
            f"Database error occured during authentication, {e}"
        ), 400


class AuthenticationController(BaseController):
    """Controller for fetching database authentication credentials."""

    def __init__(self):
        """Init the class."""
        super().__init__()

    def check_users(self, google_id: str):
        """Check if the user is in the users table."""
        session = self.get_session()
        users = session.query(User).all()

        if google_id in [user.google_uid for user in users]:
            session.close()
            return True

        session.close()
        return False

    def login_user(self, uid: str) -> Dict[str, str]:
        """Return a JTW for authorization."""
        # access token generation
        iat = int(datetime.now(UTC).timestamp())
        exp = int((datetime.now(UTC) + timedelta(hours=1)).timestamp())

        payload = {"uid": str(uid), "iat": iat, "exp": exp}

        auth_token = encode(payload, SECRET_KEY, algorithm="HS512")

        # refresh token generation
        refresh_id = random.getrandbits(32)
        iat = int(datetime.now(UTC).timestamp())
        exp = int((datetime.now(UTC) + timedelta(days=30)).timestamp())

        payload = {"uid": str(uid), "refresh": refresh_id, "iat": iat, "exp": exp}

        refresh_token = encode(payload, SECRET_KEY, algorithm="HS512")

        session = self.get_session()
        token = Token(uid=uid, refresh_id=refresh_id)
        session.add(token)
        session.commit()
        session.close()

        return auth_token, refresh_token

    def get_user(self, google_uid):
        """Return the user id with the matching google_uid."""
        session = self.get_session()
        user = session.query(User).where(User.google_uid == google_uid).one_or_none()
        if not user:
            session.close()
            return
        uid = user.id
        session.close()
        return uid

    def register_user(self, credentials: UserCredentials, id_info: any) -> str:
        """Register a new user using the provided credentials.

        Create a new credentials in the database based on the provided credentials.

        Args:
            credentials: The account's credentials
            id_info: (optional) The account's Google information

        Returns: The user's id in the database
        """
        keys = ["username", "password", "user_type"]
        valid_keys = all(key in credentials for key in keys)
        if not valid_keys:
            raise TypeError("Invalid credentials.")

        session = self.get_session()
        user = User(
            google_uid=id_info["sub"],
            email=credentials["username"],
            password=credentials["password"],
        )
        session.add(user)
        session.commit()
        session.refresh()
        user_id = user.id
        session.close()

        return str(user_id)

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

        session = self.get_session()
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
