"""Module containing utility functions for use with unittest."""

from datetime import datetime, timedelta, UTC
from jwt import encode


def generate_jwt(uid, iat=None, exp=None, secret="KU-Seek"):
    """Generate a JWT with the given fields."""
    if not iat:
        iat = int(datetime.now(UTC).timestamp())

    if not exp:
        exp = int((datetime.now(UTC) + timedelta(hours=1)).timestamp())

    payload = {"uid": str(uid), "iat": iat, "exp": exp}

    return encode(payload, secret, algorithm="HS512")
