"""
Its a custom logger class o_o .

In case that your have stumbled upon this sacred module and 
wondering why I would name the folder this long.
I, at first, had originally named this folder 'logging' and 
I figured this would conflict with the inner minds of the 
higher beings, Python, by using the same name as its 
default package, logging.
"""

import logging
import logging.config
import threading


_KW_ADAPTER = None
_LOCK = threading.RLock()

class KwAdapter(logging.LoggerAdapter):
    """
    Adapter for the logger to be able to accept kwargs.
    This damned thing is also a singleton because I want to control
    logger behavior from app.py.
    """
    def process(self, msg, kwargs):
        """Adapter function for logger."""
        extra = kwargs.pop("extra", {})
        extra.update(kwargs)
        return msg, {"extra": extra}


class OptionalUserFormatter(logging.Formatter):
    """Formatter for logger."""

    def format(self, record):
        """Format logging message if 'user' kwarg is passed to it."""
        record.user_prefix = ""
        if hasattr(record, "user"):
            record.user_prefix = f"User: {getattr(record, 'user')} - "

        return super().format(record)


def get_logger(name=None, extra=None):
    global _KW_ADAPTER
    with _LOCK:
        if _KW_ADAPTER is None:
            _KW_ADAPTER = KwAdapter(logging.getLogger(name), extra or {})
        else:
            if name is not None:
                _KW_ADAPTER.logger = logging.getLogger(name)
            if extra:
                _KW_ADAPTER.extra.update(extra)
        return _KW_ADAPTER
