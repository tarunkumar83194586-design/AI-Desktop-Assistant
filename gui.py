# gui.py
"""GUI foundation for the AI Desktop Assistant (Phase 1).

Provides a minimal Tkinter window with a placeholder chat area, a menu
allowing theme toggling, and integrates the ``ThemeManager``.
All UI logic is encapsulated in the ``App`` class to keep the module
import‑friendly for testing.
"""

# Assistant name constant
ASSISTANT_NAME = "AI Desktop Assistant"

from typing import List, Dict
import threading
import tkinter as tk
import logging
from tkinter import scrolledtext, Menu

from config import Config, get_config
from ai_engine import AIEngine
from theme_manager import ThemeManager


class App:
    """Main application class.

    Parameters
    ----------
    config: Config
        Loaded configuration instance.
    """

    def __init__(self, config: Config):
        self.config = config
        self.root = tk.Tk()
        self.root.title("AI Desktop Assistant")
        self.root.geometry(f"{config.window_width}x{config.window_height}")

        # Initialise theme manager before building widgets so defaults apply.
        self.theme_manager = ThemeManager(self.root, initial_theme=config.theme)

        # Initialise AI engine
        self.ai_engine = AIEngine()
        # Keep a simple list of message dicts for the conversation
        self._messages: List[Dict[str, str]] = []
        self._request_in_progress = False

        self._build_widgets()
        self._setup_menu()
        logging.debug("GUI initialised with theme=%s", config.theme)


    def _build_widgets(self) -> None:
        """Create the main UI components.
        """
        # Chat display – read‑only scrolled text.
        self.chat_display = scrolledtext.ScrolledText(self.root, state="disabled", wrap="word")
        self.chat_display.pack(expand=True, fill="both", padx=5, pady=5)

        # Entry box for user input (placeholder, not functional yet).
        self.entry = tk.Entry(self.root)
        self.entry.pack(fill="x", padx=5, pady=5)
        self.entry.bind("<Return>", self._on_enter)

    def _setup_menu(self) -> None:
        menubar = Menu(self.root)
        view_menu = Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Dark/Light Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view_menu)
        self.root.config(menu=menubar)

    def toggle_theme(self) -> None:
        """Switch theme and persist the change to the config object.
        """
        self.theme_manager.toggle_theme()
        # Update config so next launch remembers the choice.
        self.config.theme = self.theme_manager.current_theme
        logging.info("Theme toggled to %s", self.theme_manager.current_theme)

    
    def _on_enter(self, event=None) -> None:
        if self._request_in_progress:
            return

        user_text = self.entry.get().strip()

        if not user_text:
            return

        self.entry.delete(0, tk.END)
        self._request_in_progress = True
        self.entry.configure(state="disabled")

        self._messages.append({
            "role": "user",
            "content": user_text
        })

        self._append_chat(f"You: {user_text}\n")

        self.chat_display.configure(state="normal")

        # Save exact position of Thinking message
        self.chat_display.mark_set(
            "response_start",
            tk.END + "-1c"
        )

        self.chat_display.insert(
            tk.END,
            f"{ASSISTANT_NAME}: Thinking...\n"
        )

        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)

        messages_snapshot = list(self._messages)

        thread = threading.Thread(
            target=self._fetch_response,
            args=(messages_snapshot,),
            daemon=True
        )

        thread.start()


    def _fetch_response(self, messages_snapshot):
        try:
            reply = self.ai_engine.get_response(messages_snapshot)
        except Exception as exc:
            logging.exception("Gemini request failed")
            reply = f"[Error contacting AI model: {exc}]"

        self.root.after(
            0,
            lambda: self._replace_thinking(reply)
        )
    def _replace_thinking(self, reply):

        self.chat_display.configure(state="normal")

        # Remove only the exact Thinking message
        self.chat_display.delete(
            "response_start",
            "end-1c"
        )

        self._messages.append({
            "role": "assistant",
            "content": reply
        })

        self.chat_display.insert(
            tk.END,
            f"{ASSISTANT_NAME}: {reply}\n"
        )

        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)

        self._request_in_progress = False
        self.entry.configure(state="normal")
        self.entry.focus_set()


        

    def _check_timeout(self, thread):
        if thread.is_alive():
            logging.warning(
                "Gemini request timed out after 30 seconds"
            )

            self._replace_thinking(
                "[Error contacting AI model: timeout]"
            )

    def _append_chat(self, text: str) -> None:
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, text)
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)

    def run(self) -> None:
        """Enter the Tkinter main loop.
        """
        logging.info("Starting GUI main loop")
        self.root.mainloop()
