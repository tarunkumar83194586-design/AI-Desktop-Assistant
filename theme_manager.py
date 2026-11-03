# theme_manager.py
"""Theme manager for AI Desktop Assistant (Phase 1).

Provides light and dark theme handling using JSON palette files located in
``assets/themes``. The manager applies the selected theme to a Tkinter root
window and can toggle between themes, persisting the choice in the
configuration object passed by the caller.

The implementation is deliberately lightweight – it uses only the Python
standard library and Tkinter.
"""

import json
import logging
import os
from pathlib import Path
import tkinter as tk

# Directory containing theme JSON files – relative to this file.
THEME_DIR = Path(__file__).parent / "assets" / "themes"

DEFAULT_LIGHT = {
    "bg": "#FFFFFF",
    "fg": "#000000",
    "entry_bg": "#F0F0F0",
    "entry_fg": "#000000",
    "button_bg": "#E0E0E0",
    "button_fg": "#000000",
}

DEFAULT_DARK = {
    "bg": "#2E2E2E",
    "fg": "#FFFFFF",
    "entry_bg": "#3C3F41",
    "entry_fg": "#FFFFFF",
    "button_bg": "#5C5C5C",
    "button_fg": "#FFFFFF",
}


class ThemeManager:
    """Load, apply and toggle UI colour themes.

    Parameters
    ----------
    root: tk.Tk
        The main Tkinter window whose colours will be updated.
    initial_theme: str, optional
        ``"light"`` or ``"dark"``. If the name does not correspond to a JSON
        file, the manager falls back to the built‑in default palette.
    """

    def __init__(self, root: tk.Tk, initial_theme: str = "light") -> None:
        self.root = root
        self.current_theme = initial_theme.lower()
        self.palettes = {
            "light": self._load_palette("light.json", DEFAULT_LIGHT),
            "dark": self._load_palette("dark.json", DEFAULT_DARK),
        }
        self.apply_theme(self.current_theme)

    def _load_palette(self, filename: str, fallback: dict) -> dict:
        """Load a theme palette from ``assets/themes``.

        If the file is missing or malformed, the supplied *fallback* dict is
        returned and a warning is logged.
        """
        path = THEME_DIR / filename
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logging.debug("Loaded theme %s from %s", filename, path)
                return data
        except FileNotFoundError:
            logging.warning("Theme file %s not found – using fallback.", path)
        except json.JSONDecodeError as exc:
            logging.warning("Invalid JSON in %s: %s – using fallback.", path, exc)
        return fallback

    def apply_theme(self, name: str) -> None:
        """Apply the named theme to the Tkinter root window.

        The method updates the background/foreground colours of the root and
        any widget that inherits those options (e.g. ``Tk`` children created
        after the call). For existing widgets we rely on Tk's ``tk_setPalette``
        which propagates colours to most standard widgets.
        """
        palette = self.palettes.get(name)
        if not palette:
            logging.error("Theme %s not recognised – keeping current.", name)
            return
        self.current_theme = name
        # Configure the root window.
        self.root.configure(bg=palette["bg"])
        # ``tk_setPalette`` updates default colours for widgets.
        self.root.tk_setPalette(
            background=palette["bg"],
            foreground=palette["fg"],
            activeBackground=palette.get("button_bg", palette["bg"]),
            activeForeground=palette.get("button_fg", palette["fg"]),
        )
        logging.info("Applied %s theme", name)

    def toggle_theme(self) -> None:
        """Switch between light and dark themes.

        The new theme becomes ``self.current_theme`` and is also applied to
        the UI. Callers are responsible for persisting the choice (e.g. writing
        it back to the configuration file).
        """
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)
