"""Module for sending csrf-tokens."""

from typing import Dict
from flask import jsonify
from flask_wtf.csrf import generate_csrf
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from decouple import config


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

    return {
        "uid": id_info['sub'],
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
    }
