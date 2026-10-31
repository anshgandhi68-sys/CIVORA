"""Structured JSON Logging System for CIVORA Core."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON with security redactions."""

    SENSITIVE_KEYS = {"password", "secret", "token", "key", "authorization", "private_key"}

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id

        if hasattr(record, "run_id"):
            log_obj["run_id"] = record.run_id

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Redact sensitive parameters if passed in record.__dict__
        for key, val in record.__dict__.items():
            if key.lower() in self.SENSITIVE_KEYS:
                log_obj[key] = "[REDACTED]"

        return json.dumps(log_obj)


def setup_logging(debug: bool = False) -> logging.Logger:
    """Configures root logger with JSONFormatter."""
    level = logging.DEBUG if debug else logging.INFO
    logger = logging.getLogger("civora")
    logger.setLevel(level)

    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()

