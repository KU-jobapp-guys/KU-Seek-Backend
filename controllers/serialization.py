"""Simple serialization helpers for controllers."""

from typing import Any
import re


def _snake_to_camel(s: str) -> str:
    parts = s.split("_")
    if not parts:
        return s
    return parts[0] + "".join(p.title() for p in parts[1:])


def camelize(obj: Any) -> Any:
    """Recursively convert dict keys from snake_case to camelCase."""
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            new_key = _snake_to_camel(k) if isinstance(k, str) else k
            new[new_key] = camelize(v)
        return new

    if isinstance(obj, (list, tuple)):
        return [camelize(i) for i in obj]

    return obj


def _camel_to_snake(s: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.replace("-", "_").lower()


def decamelize(obj: Any) -> Any:
    """Recursively convert dict/list keys from camelCase to snake_case."""
    if hasattr(obj, "items"):
        new = {}
        for k, v in obj.items():
            new_key = _camel_to_snake(k) if isinstance(k, str) else k
            new[new_key] = decamelize(v)
        return new

    if isinstance(obj, (list, tuple)):
        return [decamelize(i) for i in obj]

    return obj
