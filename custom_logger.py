"""Custom KwAdapter for logging."""

import logging
import logging.config
from pathlib import Path
from dotenv import load_dotenv
import threading
import os

load_dotenv()

LOGGING_CONF = Path(__file__).with_name("logging.conf")
logging.config.fileConfig(LOGGING_CONF, disable_existing_loggers=False)

_DEFAULT_LOGGER_NAME = os.getenv("LOGGER")
_LOCK = threading.RLock()
_ADAPTER = None


class KwAdapter(logging.LoggerAdapter):
    """Key word adapter to take kwargs from logging function."""

    def process(self, msg, kwargs):
        """Process kwargs from logging function."""
        extra = kwargs.pop("extra", {})
        user = kwargs.pop("user", None)
        if user is not None:
            extra["user"] = user
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger():
    """Get the selected logger from app.py."""
    global _ADAPTER
    name = _DEFAULT_LOGGER_NAME
    with _LOCK:
        if _ADAPTER is None:
            _ADAPTER = KwAdapter(logging.getLogger(name), {})
        else:
            _ADAPTER.logger = logging.getLogger(name)
        return _ADAPTER
