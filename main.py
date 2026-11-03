# main.py
"""Application entry point for the AI Desktop Assistant (Phase 1).

- Sets up logging.
- Loads configuration.
- Starts the GUI application.

All heavy lifting is delegated to dedicated modules to keep the codebase clean and testable.
"""

import sys
from pathlib import Path

# Ensure the project root is on sys.path for module imports when run from the project directory.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from logging_setup import setup_logging
from config import get_config
from gui import App


def main() -> None:
    """Run the desktop assistant.

    All uncaught exceptions are logged via the global logging configuration.
    """
    try:
        # Initialise the logging system – writes to logs/errors.log
        cfg = get_config()
        setup_logging(level=cfg.log_level)
        # Load configuration (uses defaults if a user config file is missing)
        config = get_config()
        # Initialise and run the GUI
        app = App(config)
        app.run()
    except Exception as exc:  # pragma: no cover – should be caught by logging as well
        import logging
        logging.exception("Fatal error in main()")
        raise

if __name__ == "__main__":
    main()
