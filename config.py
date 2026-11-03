# config.py
"""Configuration loader for AI Desktop Assistant (Phase 1).

Uses a simple dataclass with default values. A user‑provided JSON file
`config/user_config.json` can override any of the defaults. The module
exposes a singleton accessor `get_config()` that returns the loaded
`Config` instance.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

import logging

DEFAULT_CONFIG = {
    "window_width": 800,
    "window_height": 600,
    "theme": "light",  # "dark" or "light"
    "language": "en",   # future use (en, hi)
    "log_level": "INFO",
    # Placeholder for API keys etc.
    "gemini_api_key": "",
}

CONFIG_DIR = Path(__file__).resolve().parent / "config"
USER_CONFIG_PATH = CONFIG_DIR / "user_config.json"

@dataclass
class Config:
    """Typed configuration container.

    Attributes match keys from ``DEFAULT_CONFIG``. Additional fields can be
    added later without breaking existing code.
    """
    window_width: int = DEFAULT_CONFIG["window_width"]
    window_height: int = DEFAULT_CONFIG["window_height"]
    theme: str = DEFAULT_CONFIG["theme"]
    language: str = DEFAULT_CONFIG["language"]
    log_level: str = DEFAULT_CONFIG["log_level"]
    gemini_api_key: str = DEFAULT_CONFIG["gemini_api_key"]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create a Config instance from a plain dict, falling back to defaults.
        """
        # Using dict.get ensures missing keys keep default values.
        return cls(
            window_width=int(data.get("window_width", cls().window_width)),
            window_height=int(data.get("window_height", cls().window_height)),
            theme=str(data.get("theme", cls().theme)),
            language=str(data.get("language", cls().language)),
            log_level=str(data.get("log_level", cls().log_level)),
            gemini_api_key=str(data.get("gemini_api_key", cls().gemini_api_key)),
        )

# Singleton holder – lazily loaded on first call.
_config_instance: Config | None = None


def _load_user_config() -> Dict[str, Any]:
    """Read the optional user configuration file.

    Returns an empty dict if the file does not exist or is malformed.
    Errors are logged but do not stop the application.
    """
    if not USER_CONFIG_PATH.is_file():
        return {}
    try:
        with USER_CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # pragma: no cover – exercised via test
        logging.getLogger(__name__).warning(
            "Failed to load user config %s: %s", USER_CONFIG_PATH, exc
        )
        return {}


def get_config() -> Config:
    """Public accessor for the global configuration.

    The function memoises the loaded configuration so repeated calls are cheap.
    """
    global _config_instance
    if _config_instance is None:
        user_cfg = _load_user_config()
        _config_instance = Config.from_dict({**DEFAULT_CONFIG, **user_cfg})
    return _config_instance
