"""AI agent orchestration: routing, tool execution, chat history."""

from __future__ import annotations

import re

from config import CHAT_HISTORY_FILE
from services.gemini_service import gemini_service
from tools.email_tool import send_email
from tools.function_tools import FUNCTION_REGISTRY, TOOL_DECLARATIONS
from utils.tool_runner import run_function_tool
from tools.notes_tool import list_notes, save_note
from tools.web_search_tool import search_jobs
from utils.json_db import JsonDatabase
from utils.logger import log_event

# Intent patterns for rule-based routing when Gemini unavailable or as boost
INTENT_PATTERNS = [
    (r"\b(search|find|look for).*(job|jobs|position|role)\b", "search_jobs"),
    (r"\b(job|jobs)\b.*\b(ai|python|react|remote|developer)\b", "search_jobs"),
    (r"\b(save|create|add).*(note)\b", "save_note"),
    (r"\b(list|show|view|get).*(notes)\b", "list_notes"),
    (r"\b(send)\b.*\b(email|mail)\b", "send_email"),
    (r"\b(calculate|calculator|math)\b", "calculator"),
    (r"\d+\s*(plus|minus|times|\*|\+|\-|\/)\s*\d+", "calculator"),
    (r"\bwhat is\b.*\d+", "calculator"),
    (r"\b(time|date|datetime|today)\b", "datetime_tool"),
    (r"\b(summarize|summary)\b", "text_summarizer"),
    (r"\b(extract|urls?|links?)\b", "url_extractor"),
    (r"\b(keywords?)\b", "keyword_extractor"),
]


class AgentService:
    def __init__(self):
        self.history_db = JsonDatabase(CHAT_HISTORY_FILE, default=[])

    def process_message(self, message: str, session_id: str | None = None) -> dict:
        session_id = session_id or "default"
        history = self._get_session_history(session_id)

        # Try Gemini with function calling
        gemini_result = gemini_service.chat(
            message,
            history=history,
            tool_declarations=TOOL_DECLARATIONS,
        )

        tool_results = []
        final_text = gemini_result.get("text")
        tool_calls = gemini_result.get("tool_calls") or []

        # Rule-based fallback if Gemini unavailable, rate-limited, or no tool calls
        gemini_failed = bool(gemini_result.get("error"))
        if not tool_calls or gemini_failed:
            intent = self._detect_intent(message)
            if intent:
                tool_calls = [{"name": intent, "args": self._infer_args(intent, message)}]

        for call in tool_calls:
            name = call.get("name")
            args = call.get("args") or {}
            result = self._execute_tool(name, args, message)
            tool_results.append({"tool": name, "result": result})

        err_lower = (final_text or "").lower()
        gemini_placeholder = final_text and (
            "not configured" in err_lower
            or "error communicating with gemini" in err_lower
            or "quota" in err_lower
            or "429" in err_lower
        )

        if tool_results and (not final_text or gemini_placeholder):
            final_text = self._format_tool_response(tool_results)
        elif tool_results and final_text:
            final_text = f"{final_text}\n\n{self._format_tool_response(tool_results)}"
        elif not final_text:
            final_text = (
                "I'm NEXEAGENT, your multi-tool AI assistant. I can search jobs, "
                "manage notes, send emails, and run utility tools. How can I help?"
            )

        self._save_turn(session_id, message, final_text, tool_results)
        log_event("info", f"Chat processed session={session_id}")

        return {
            "response": final_text,
            "tool_results": tool_results,
            "session_id": session_id,
        }

    def _execute_tool(self, name: str | None, args: dict, message: str) -> dict:
        if not name:
            return {"error": "Unknown tool"}

        try:
            if name == "search_jobs":
                query = args.get("query") or self._extract_query(message) or "AI developer remote"
                limit = int(args.get("limit", 10))
                return search_jobs(query, limit)

            if name == "save_note":
                title = args.get("title") or "Agent Note"
                content = args.get("content") or message
                return save_note(title, content, args.get("tags"))

            if name == "list_notes":
                return list_notes()

            if name == "send_email":
                return send_email(
                    args.get("to_email", ""),
                    args.get("subject", "NEXEAGENT Notification"),
                    args.get("body", message),
                )

            if name in FUNCTION_REGISTRY:
                return run_function_tool(name, args, fallback_text=message)

            return {"error": f"Tool '{name}' not implemented"}
        except Exception as exc:
            log_event("error", f"Tool {name} failed: {exc}")
            return {"error": str(exc)}

    def _detect_intent(self, message: str) -> str | None:
        lower = message.lower()
        for pattern, intent in INTENT_PATTERNS:
            if re.search(pattern, lower):
                return intent
        return None

    def _infer_args(self, intent: str, message: str) -> dict:
        if intent == "search_jobs":
            return {"query": self._extract_query(message) or "AI automation developer remote"}
        if intent == "save_note":
            return {"title": "Chat Note", "content": message}
        if intent == "text_summarizer":
            return {"text": message}
        if intent == "calculator":
            expr = message.lower()
            expr = re.sub(r"\bplus\b", "+", expr)
            expr = re.sub(r"\bminus\b", "-", expr)
            expr = re.sub(r"\btimes\b", "*", expr)
            expr = re.sub(r"\bdivided by\b", "/", expr)
            match = re.search(r"[\d\s+\-*/().]+", expr)
            return {"expression": match.group(0).strip() if match else "0"}
        return {}

    def _extract_query(self, message: str) -> str | None:
        for kw in ["for", "search", "find", "jobs"]:
            if kw in message.lower():
                parts = re.split(rf"\b{kw}\b", message, flags=re.IGNORECASE)
                if len(parts) > 1 and parts[-1].strip():
                    return parts[-1].strip(" :.,!?")
        return None

    def _format_tool_response(self, tool_results: list) -> str:
        parts = []
        for tr in tool_results:
            name = tr.get("tool")
            result = tr.get("result") or {}
            if name == "search_jobs" and result.get("jobs"):
                parts.append(result.get("summary") or f"Found {result.get('count', 0)} jobs.")
            elif name == "list_notes":
                parts.append(f"You have {result.get('count', 0)} saved notes.")
            elif name == "save_note" and result.get("success"):
                parts.append(f"Note saved: {result['note'].get('title')}")
            elif name == "send_email":
                parts.append(result.get("message", "Email processed."))
            elif "summary" in result:
                parts.append(result["summary"])
            elif "result" in result:
                parts.append(f"Result: {result['result']}")
            elif "formatted" in result:
                parts.append(result.get("formatted", "")[:500])
            else:
                parts.append(str(result)[:800])
        return "\n\n".join(parts) if parts else "Done."

    def _get_session_history(self, session_id: str) -> list[dict]:
        all_history = self.history_db.read()
        session = next(
            (s for s in all_history if s.get("session_id") == session_id),
            None,
        )
        return session.get("messages", []) if session else []

    def _save_turn(
        self,
        session_id: str,
        user_msg: str,
        assistant_msg: str,
        tool_results: list,
    ) -> None:
        all_history = self.history_db.read()
        session = next(
            (s for s in all_history if s.get("session_id") == session_id),
            None,
        )
        if not session:
            session = {"session_id": session_id, "messages": []}
            all_history.append(session)

        session["messages"].append({"role": "user", "content": user_msg})
        session["messages"].append({
            "role": "assistant",
            "content": assistant_msg,
            "tools": tool_results,
        })
        session["messages"] = session["messages"][-50:]

        for i, s in enumerate(all_history):
            if s.get("session_id") == session_id:
                all_history[i] = session
                break

        self.history_db.write(all_history[-20:])

    def get_history(self, session_id: str = "default") -> list[dict]:
        return self._get_session_history(session_id)

    def list_sessions(self) -> list[dict]:
        return [
            {
                "session_id": s.get("session_id"),
                "message_count": len(s.get("messages", [])),
            }
            for s in self.history_db.read()
        ]


agent_service = AgentService()
