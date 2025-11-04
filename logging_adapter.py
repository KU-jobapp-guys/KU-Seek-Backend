import logging

class OptionalUserFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, "user"):
            record.user_prefix = f"User:{record.user} - "
        elif not hasattr(record, "user_prefix"):
            record.user_prefix = ""
        return super().format(record)
