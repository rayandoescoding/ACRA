import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """
    Custom logging Formatter that outputs logs in structured JSON format.
    """

    def format(self, record: logging.LogRecord) -> str:
        # Construct standard log structure
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Exclude standard attributes to capture custom extra attributes
        standard_attrs = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "module",
            "msecs", "message", "msg", "name", "pathname", "process",
            "processName", "relativeCreated", "stack_info", "thread",
            "threadName"
        }

        for key, val in record.__dict__.items():
            if key not in standard_attrs:
                log_record[key] = val

        return json.dumps(log_record)


def setup_logging() -> None:
    """
    Configures standard application logging with consistent JSON output.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,  # Override default system log configuration if any
    )

