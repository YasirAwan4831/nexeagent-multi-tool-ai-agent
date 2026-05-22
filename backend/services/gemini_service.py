"""Google Gemini API integration — set GEMINI_API_KEY in backend/.env"""

from __future__ import annotations

import re
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT_FILE
from utils.logger import log_event

# Fallback models if primary is unavailable for this API key
MODEL_FALLBACKS = [
    GEMINI_MODEL,
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
]


class GeminiService:
    def __init__(self):
        self._configured = bool(GEMINI_API_KEY)
        self._active_model = GEMINI_MODEL
        if self._configured:
            genai.configure(api_key=GEMINI_API_KEY)
            self._active_model = self._resolve_model()
        self._system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        try:
            return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
        except FileNotFoundError:
            return "You are NEXEAGENT, a helpful multi-tool AI automation assistant."

    def _resolve_model(self) -> str:
        """Pick first model that responds for this API key."""
        trusted = {"gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"}
        if GEMINI_MODEL in trusted:
            log_event("info", f"Gemini model configured: {GEMINI_MODEL}")
            return GEMINI_MODEL

        for model_name in MODEL_FALLBACKS:
            if not model_name:
                continue
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Reply with OK only.")
                if response and response.text:
                    log_event("info", f"Gemini model active: {model_name}")
                    return model_name
            except Exception as exc:
                log_event("warning", f"Gemini model {model_name} unavailable: {exc}")
        log_event("warning", f"Using configured model without probe: {GEMINI_MODEL}")
        return GEMINI_MODEL or "gemini-2.5-flash"

    @property
    def is_available(self) -> bool:
        return self._configured

    @property
    def active_model(self) -> str:
        return self._active_model

    def _get_model(self, tools: list | None = None):
        if not self._configured:
            raise RuntimeError(
                "Gemini API key not configured. Set GEMINI_API_KEY in backend/.env"
            )
        kwargs = {
            "model_name": self._active_model,
            "system_instruction": self._system_prompt,
        }
        if tools:
            kwargs["tools"] = tools
        return genai.GenerativeModel(**kwargs)

    @staticmethod
    def _parse_function_args(args) -> dict:
        if not args:
            return {}
        try:
            return dict(args)
        except (TypeError, ValueError):
            return {k: args[k] for k in args.keys()}

    def _build_tools(self, tool_declarations: list[dict]) -> list | None:
        if not tool_declarations:
            return None
        functions = []
        for t in tool_declarations:
            params = t.get("parameters") or {"type": "object", "properties": {}}
            if params.get("type") != "object":
                params = {"type": "object", "properties": params.get("properties", {})}
            if "properties" not in params:
                params["properties"] = {}
            functions.append(
                FunctionDeclaration(
                    name=t["name"],
                    description=t.get("description", ""),
                    parameters=params,
                )
            )
        return [Tool(function_declarations=functions)]

    def chat(
        self,
        message: str,
        history: list[dict] | None = None,
        tool_declarations: list[dict] | None = None,
    ) -> dict:
        if not self._configured:
            return {
                "text": (
                    "Gemini is not configured. Add GEMINI_API_KEY to backend/.env "
                    "and restart the server."
                ),
                "tool_calls": [],
                "error": "missing_api_key",
            }

        try:
            tools = self._build_tools(tool_declarations or [])
            model = self._get_model(tools=tools)
            chat = model.start_chat(history=self._format_history(history or []))
            response = self._send_with_retry(chat, message)

            tool_calls = []
            text_parts = []

            if not response.candidates:
                block = getattr(response, "prompt_feedback", None)
                return {
                    "text": f"No response from Gemini. Feedback: {block}",
                    "tool_calls": [],
                    "error": "empty_response",
                }

            content = response.candidates[0].content
            if not content or not content.parts:
                return {
                    "text": "Empty response from Gemini.",
                    "tool_calls": [],
                    "error": "empty_parts",
                }

            for part in content.parts:
                if hasattr(part, "text") and part.text:
                    text_parts.append(part.text)
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    tool_calls.append(
                        {"name": fc.name, "args": self._parse_function_args(fc.args)}
                    )

            return {
                "text": "\n".join(text_parts).strip() or None,
                "tool_calls": tool_calls,
                "raw": response,
            }
        except Exception as exc:
            log_event("error", f"Gemini API error: {exc}")
            # Retry without tools if schema caused failure
            if tool_declarations:
                try:
                    model = self._get_model(tools=None)
                    response = model.generate_content(message)
                    if response.text:
                        return {
                            "text": response.text.strip(),
                            "tool_calls": [],
                            "raw": response,
                        }
                except Exception:
                    pass
            return {
                "text": f"I encountered an error communicating with Gemini: {exc}",
                "tool_calls": [],
                "error": str(exc),
            }

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        if not self._configured:
            return text[:500] + ("..." if len(text) > 500 else "")

        model = self._get_model()
        prompt = (
            f"Summarize the following in at most {max_sentences} clear sentences:\n\n{text}"
        )
        try:
            response = model.generate_content(prompt)
            if response.text:
                return response.text.strip()
            return text[:500] + ("..." if len(text) > 500 else "")
        except Exception as exc:
            log_event("warning", f"Summarize fallback: {exc}")
            return text[:500]

    @staticmethod
    def _send_with_retry(chat, message: str, max_retries: int = 2):
        last_exc = None
        for attempt in range(max_retries + 1):
            try:
                return chat.send_message(message)
            except Exception as exc:
                last_exc = exc
                err = str(exc)
                if "429" in err or "quota" in err.lower():
                    delay_match = re.search(r"retry in (\d+(?:\.\d+)?)s", err, re.I)
                    delay = float(delay_match.group(1)) + 1 if delay_match else 20
                    if attempt < max_retries:
                        log_event("warning", f"Gemini rate limit, retry in {delay}s")
                        time.sleep(min(delay, 30))
                        continue
                raise
        raise last_exc

    def _format_history(self, history: list[dict]) -> list:
        formatted = []
        for item in history[-10:]:
            role = "user" if item.get("role") == "user" else "model"
            parts = item.get("content", "")
            if parts:
                formatted.append({"role": role, "parts": [parts]})
        return formatted


gemini_service = GeminiService()
