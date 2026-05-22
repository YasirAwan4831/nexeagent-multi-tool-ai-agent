"""Centralized logging for the NEXEAGENT backend."""

import logging
import sys
from datetime import datetime, timezone

from config import LOGS_FILE
from utils.json_db import JsonDatabase


def setup_logger(name: str = "nexeagent") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger


logger = setup_logger()


def log_event(level: str, message: str, context: dict | None = None) -> None:
    """Write structured log entry to logs.json and Python logger."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        "context": context or {},
    }
    try:
        db = JsonDatabase(LOGS_FILE, default=[])
        logs = db.read()
        if not isinstance(logs, list):
            logs = []
        logs.append(entry)
        if len(logs) > 500:
            logs = logs[-500:]
        db.write(logs)
    except Exception as exc:
        logger.warning("Failed to persist log entry: %s", exc)

    getattr(logger, level.lower(), logger.info)(message)
