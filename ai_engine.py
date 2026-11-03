
# ai_engine.py
"""Gemini AI Engine using the new Google GenAI SDK."""

import logging
import time
from typing import List, Dict

_logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-3.5-flash-lite"


class AIEngine:
    """Wrapper around Google's Gemini AI model."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None
    ):
        from config import get_config

        cfg = get_config()

        self.api_key = api_key or cfg.gemini_api_key
        self.model_name = model_name or DEFAULT_MODEL
        self._client = None

        if not self.api_key:
            raise RuntimeError(
                "Gemini API key is not set."
            )

        self._setup_client()

    def _setup_client(self) -> None:
        """Initialize Gemini client."""

        try:
            from google import genai

        except ImportError as exc:
            raise RuntimeError(
                "Install the new SDK using: "
                "pip install -U google-genai"
            ) from exc

        try:
            self._client = genai.Client(
                api_key=self.api_key
            )

            _logger.info(
                "Gemini client initialized: %s",
                self.model_name
            )

        except Exception as exc:
            _logger.exception(
                "Gemini client initialization failed"
            )
            raise RuntimeError(
                f"Client initialization failed: {exc}"
            ) from exc

    
    def get_response(
            self,
            messages: List[Dict[str, str]]
        ) -> str:
        """Send conversation history and return Gemini response."""

        if not messages:
            return ""

        if self._client is None:
            self._setup_client()

        contents = []

        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "").strip()

            if not content:
                continue

            if role == "assistant":
                role = "model"
            elif role != "user":
                continue

            contents.append({
                "role": role,
                "parts": [{"text": content}]
            })

        if not contents:
            return ""

        try:
            _logger.info("Sending request to Gemini...")

            start_time = time.perf_counter()

            for attempt in range(3):
                try:
                   
                    response = self._client.models.generate_content(
                        model=self.model_name,
                        contents=contents,
                        config={
                            "temperature": 0.7,
                            "max_output_tokens": 1024
                        }
                    )
                   

                    elapsed = time.perf_counter() - start_time

                    reply = response.text

                    _logger.info(
                        "Gemini response received in %.2f seconds",
                        elapsed
                    )

                    if not reply or not reply.strip():
                        return "Gemini returned an empty response."

                    return reply.strip()

                except Exception as e:

                    if "503" in str(e):
                        _logger.warning(
                            "Gemini busy. Retrying (%d/3)...",
                            attempt + 1
                        )
                        time.sleep(5)
                        continue

                    raise

            return (
                "Gemini servers are busy right now. "
                "Please try again in a minute."
            )

        except Exception as exc:
            _logger.exception("Error communicating with Gemini")
            return f"[Error contacting AI model: {exc}]"
