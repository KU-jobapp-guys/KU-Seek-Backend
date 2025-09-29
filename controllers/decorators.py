"""Module for API decorators."""

from functools import wraps
from flask import request
from swagger_server.openapi_server import models
from jwt import decode
from decouple import config
from datetime import datetime
from .db_controller import BaseController
from .models import User


SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


def login_required(func):
    """Check if the user is authenticated via JWT credentials in the cookie."""

    @wraps(func)
    def run_function(*args, **kwargs):
        jwt_auth_token = request.headers.get("access_token")

        if not jwt_auth_token:
            return models.ErrorMessage("User is not authenticated."), 401

        try:
            token_info = decode(
                jwt=jwt_auth_token, key=SECRET_KEY, algorithms=["HS512"]
            )
            if datetime.fromtimestamp(token_info["exp"]) <= datetime.now():
                return models.ErrorMessage("Expired authentication token."), 403

        except Exception as e:
            return models.ErrorMessage(f"Invalid authentication token., {e}"), 403

        # authentication successful, serve the API.
        return func(*args, **kwargs)

    return run_function


def role_required(func, roles: list[str] = []):
    """
    Check if the user has a valid role to use the API.

    Args:
        roles: A list of roles that are allowed to use the API.
               An empty list will allow access for all roles.
    """

    def decorator(func):
        @wraps(func)
        def run_function(*args, **kwargs):
            jwt_auth_token = request.headers.get("access_token")

            if not jwt_auth_token:
                return models.ErrorMessage("User is not authenticated."), 401

            try:
                token_info = decode(
                    jwt=jwt_auth_token, key=SECRET_KEY, algorithms=["HS512"]
                )
                if datetime.fromtimestamp(token_info["exp"]) <= datetime.now():
                    return models.ErrorMessage("Expired authentication token."), 403

            except Exception as e:
                return models.ErrorMessage(f"Invalid authentication token., {e}"), 403

            # fetch the user's role and validate
            session = BaseController().get_session()

            user = session.query(User).where(User.id == token_info["uid"]).one_or_none()
            if not user:
                session.close()
                return models.ErrorMessage("Invalid user."), 403

            if roles:
                if user.type not in roles:
                    session.close()
                    return models.ErrorMessage("User does not have authorization."), 403

            # authorization successful, serve the API.
            return func(*args, **kwargs)

        return run_function

    return decorator
