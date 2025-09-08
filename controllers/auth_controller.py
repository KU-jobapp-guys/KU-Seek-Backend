"""Module for sending csrf-tokens."""

import random
from typing import Dict, TypedDict
from flask import jsonify
from flask_wtf.csrf import generate_csrf
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from decouple import config
from .db_controller import BaseController
from jwt import encode
from swagger_server.openapi_server import models
from datetime import datetime, timedelta, UTC


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

        return models.Token(user_jwt, refresh)
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
        query = "SELECT * FROM user_google_auth_info;"
        result = self.execute_query(query, fetchall=True)

        if google_id in [row["google_uid"] for row in result]:
            return True
        return False

    def login_user(self, uid: str) -> Dict[str, str]:
        """Return a JTW for authorization."""
        # access token generation
        iat = (datetime.now(UTC).isoformat(),)
        exp = ((datetime.now(UTC) + timedelta(hours=1)).isoformat(),)

        payload = {"uid": uid, "iat": iat, "exp": exp}

        auth_token = encode(payload, SECRET_KEY, algorithm="HS512")

        # refresh token generation
        refresh_id = random.getrandbits(32)
        iat = (datetime.now(UTC).isoformat(),)
        exp = ((datetime.now(UTC) + timedelta(days=30)).isoformat(),)

        payload = {"uid": uid, "refresh": refresh_id, "iat": iat, "exp": exp}

        refresh_token = encode(payload, SECRET_KEY, algorithm="HS512")
        query = f"""
                INSERT INTO tokens
                (user_id, refresh_id) 
                VALUES ({uid}, {refresh_id});
                """
        self.execute_query(query, commit=True)

        return auth_token, refresh_token

    def get_user(self, google_uid):
        """Return the user id with the matching google_uid."""
        query = f"""
                SELECT * FROM user_google_auth_info WHERE google_uid = '{google_uid}'
                """
        user = self.execute_query(query, fetchone=True)
        return user["user_id"]

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

        query = f"""
                INSERT INTO users (username, password, user_type) 
                VALUES ('{credentials["username"]}',
                        '{credentials["password"]}',
                        '{credentials["user_type"]}');
                """
        self.execute_query(query, commit=True)

        query = f"""
                SELECT * FROM users WHERE 
                username = '{credentials["username"]}' AND
                password = '{credentials["password"]}' AND
                user_type = '{credentials["user_type"]}';
                """
        user = self.execute_query(query, fetchone=True)

        query = f"""
                INSERT INTO user_google_auth_info 
                (user_id, google_uid, email, picture, first_name, last_name) 
                VALUES ({user["id"]},
                        '{id_info["sub"]}',
                        '{id_info["email"]}',
                        '{id_info["picture"]}',
                        '{id_info["given_name"]}',
                        '{id_info["family_name"]}');
                """
        self.execute_query(query, commit=True)
        return user["id"]
