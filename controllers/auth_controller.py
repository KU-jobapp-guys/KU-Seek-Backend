"""Module for sending csrf-tokens."""

from flask import jsonify
from flask_wtf.csrf import generate_csrf


def get_csrf_token():
    """
    Return a CSRF-token.

    Creates a CSRF-token using the flask-WTF library for form validation.

    Returns: A JSON with the csrf-token field.
    """
    return jsonify(csrf_token=generate_csrf())
    