"""Module for API decorators."""

from functools import wraps
from flask import request
from swagger_server.openapi_server import models
from jwt import decode
from decouple import config
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from .models import User
from uuid import UUID
from flask import current_app
from typing import Literal


SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


def login_required(func):
    """Check if the user is authenticated via JWT credentials in the cookie."""

    @wraps(func)
    def run_function(*args, **kwargs):
        jwt_auth_token = request.headers.get("access_token")

        if not jwt_auth_token:
            return models.ErrorMessage("User is not authenticated."), 401

        try:
            decode(jwt=jwt_auth_token, key=SECRET_KEY, algorithms=["HS512"])

        except InvalidSignatureError:
            return models.ErrorMessage("Invalid authentication token provided"), 403
        except ExpiredSignatureError:
            return models.ErrorMessage("Token is expired"), 403
        except Exception as e:
            return models.ErrorMessage(f"Invalid authentication token, {e}"), 403

        # authentication successful
        return func(*args, **kwargs)

    return run_function


def role_required(roles: list[Literal["Student", "Company"]] = []):
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

            except InvalidSignatureError:
                return models.ErrorMessage("Invalid authentication token provided"), 403
            except ExpiredSignatureError:
                return models.ErrorMessage("Token is expired"), 403
            except Exception as e:
                return models.ErrorMessage(f"Invalid authentication token, {e}"), 403

            # fetch the user's role and validate
            session = current_app.config["Database"].get_session()

            user = (
                session.query(User)
                .where(User.id == UUID(token_info["uid"]))
                .one_or_none()
            )

            if not user:
                session.close()
                return models.ErrorMessage("Invalid user."), 403

            if user.type.value not in roles:
                session.close()
                return models.ErrorMessage("User does not have authorization."), 403

            session.close()
            # Authorization successful

            return func(*args, **kwargs)

        return run_function

    return decorator


def rate_limit(func):
    """Apply rate-limiting to an API endpoint."""

    @wraps(func)
    def run_function(*args, **kwargs):
        jwt_auth_token = request.headers.get("access_token")

        if not jwt_auth_token:
            return models.ErrorMessage("User is not authenticated."), 401

        try:
            token_info = decode(
                jwt=jwt_auth_token, key=SECRET_KEY, algorithms=["HS512"]
            )

        except InvalidSignatureError:
            return models.ErrorMessage("Invalid authentication token provided"), 403
        except ExpiredSignatureError:
            return models.ErrorMessage("Token is expired"), 403
        except Exception as e:
            return models.ErrorMessage(f"Invalid authentication token, {e}"), 403

        # authentication successful

        rate_limiter = current_app.config["RateLimiter"]
        if not rate_limiter.request(token_info["uid"]):
            raise Warning("Too many requests. Please renew login session.")
        return func(*args, **kwargs)

    return run_function


def login_rate_limit(func):
    """Apply login rate-limiting to an API endpoint."""

    @wraps(func)
    def run_function(*args, **kwargs):
        ip_address = request.remote_addr

        rate_limiter = current_app.config["RateLimiter"]
        if not rate_limiter.attempt_login(ip_address):
            return models.ErrorMessage(
                "Too many login attempts. Please try again later."
            ), 429

        return func(*args, **kwargs)

    return run_function


def unban_user(func):
    """Unban a user from the rate limiter."""

    @wraps(func)
    def run_function(*args, **kwargs):
        return_values = func(*args, **kwargs)
        rate_limiter = current_app.config["RateLimiter"]
        rate_limiter.unban_user(return_values[3])
        return return_values

    return run_function
