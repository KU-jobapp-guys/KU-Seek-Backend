"""Module for sending csrf-tokens."""

from typing import Dict, TypedDict
from flask import jsonify
from flask_wtf.csrf import generate_csrf
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from decouple import config
from db_controller import BaseController
from jwt import encode
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
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=["openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"],
        redirect_uri=redirect_uri,
    )

    # Exchange the authorization code for tokens
    flow.fetch_token(code=body["code"])

    credentials = flow.credentials

    # Decode JWT using Google ID Token helper
    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
        requests.Request(),
        audience=config("CLIENT_ID", default="very-secret-client-id")
    )

    auth_controller = AuthenticationController()

    is_registered = auth_controller.check_users(id_info['sub'])

    user_jwt = {}
    if is_registered:
        user_jwt = auth_controller.login_user(id_info['sub'])
    else:
        auth_controller.register_user(id_info['email'], id_info['at_hash'], 'company')
        user_jwt = auth_controller.login_user(id_info['sub'])

    return user_jwt


class AuthenticationController(BaseController):
    """Controller for fetching database authentication credentials."""

    def __init__(self):
        """Init the class."""
        super().__init__()

    def check_users(self, google_id: str):
        """Check if the user is in the users table."""
        query = "SELECT * FROM user_google_auth_info;"
        result = self.execute_query(query, fetchall=True)
        
        if google_id in [row for row in result['google_uid']]: 
            return True
        return False
    
    def login_user(self, uid: str) -> Dict[str, str]:
        """Return a JTW for authorization."""
        refresh = {'iat': datetime.now(UTC),
                   'exp': datetime.now(UTC) + timedelta(hours=1)}

        payload = {'uid': uid,
                   'refresh_token': refresh
                   }
        
        auth_token = encode(payload, SECRET_KEY, algorithm="HS512")

        return {"user_token" : auth_token}


    def register_user(self, credentials: UserCredentials):
        """Register a new user using the provided credentials.
        
        Create a new credentials in the database based on the provided credentials.

        Args:
            credentials: The account's credentials
        """
        keys = ["username", "password", "user_type"]
        valid_keys = all(key in credentials for key in keys)
        if not valid_keys:
            raise TypeError("Invalid credentials.")

        query = f"""
                INSERT INTO users (username, password, user_type) 
                VALUES ('{credentials['username']}',
                        '{credentials['password']}',
                        '{credentials['user_type']}');
                """
        return self.execute_query(query, commit=True)

