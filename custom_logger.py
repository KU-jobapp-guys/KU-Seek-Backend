import logging
import logging.config
from pathlib import Path
import threading
from app import LOGGER

LOGGING_CONF = Path(__file__).with_name("logging.conf")
logging.config.fileConfig(LOGGING_CONF, disable_existing_loggers=False)

_DEFAULT_LOGGER_NAME = LOGGER
_LOCK = threading.RLock()
_ADAPTER = None

class KwAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.pop("extra", {})
        user = kwargs.pop("user", None)
        if user is not None:
            extra["user"] = user
        kwargs["extra"] = extra
        return msg, kwargs

def get_logger(name=None):
    global _ADAPTER
    if name is None:
        name = _DEFAULT_LOGGER_NAME
    with _LOCK:
        if _ADAPTER is None:
            _ADAPTER = KwAdapter(logging.getLogger(name), {})
        else:
            _ADAPTER.logger = logging.getLogger(name)
        return _ADAPTER
