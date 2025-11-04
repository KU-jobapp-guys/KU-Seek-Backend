"""Custom formatter for logging."""

import logging


class OptionalUserFormatter(logging.Formatter):
    """Custom formatter for logging."""

    def format(self, record):
        """Format function for 'user' kwarg."""
        if hasattr(record, "user"):
            record.user_prefix = f"User:{record.user} - "
        elif not hasattr(record, "user_prefix"):
            record.user_prefix = ""
        return super().format(record)
