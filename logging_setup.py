# logging_setup.py
"""Centralised logging configuration for the AI Desktop Assistant.

Uses the standard library ``logging`` module with a rotating file handler.
All modules import ``setup_logging`` and call it once at start‑up.
"""

import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE = LOG_DIR / "errors.log"

def setup_logging(level: str = "INFO") -> None:
    """Configure root logger.

    Parameters
    ----------
    level: str, optional
        Logging level name (e.g., "DEBUG", "INFO"). Defaults to "INFO".
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level.upper())
    # Remove any existing handlers to avoid duplicate logs when re‑executed
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
    # Also output warnings to console for development convenience
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    logging.debug("Logging initialized – level=%s, file=%s", level, LOG_FILE)
