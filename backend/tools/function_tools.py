"""Utility function tools for the AI agent."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from services.gemini_service import gemini_service
from utils.helpers import extract_urls


def calculator(expression: str) -> dict:
    """Safe math evaluation (numbers and basic operators only)."""
    allowed = re.compile(r"^[\d\s+\-*/().%]+$")
    if not allowed.match(expression):
        return {"error": "Invalid characters in expression"}
    try:
        # Replace ^ with ** for power
        expr = expression.replace("^", "**")
        result = eval(expr, {"__builtins__": {}}, {})  # noqa: S307 — restricted chars
        return {"expression": expression, "result": result}
    except Exception as exc:
        return {"error": str(exc)}


def datetime_tool(action: str = "now", timezone_name: str = "UTC") -> dict:
    now = datetime.now(timezone.utc)
    return {
        "action": action,
        "iso": now.isoformat(),
        "formatted": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "timezone": timezone_name,
        "weekday": now.strftime("%A"),
    }


def url_extractor(text: str) -> dict:
    urls = extract_urls(text)
    return {"count": len(urls), "urls": urls}


def text_summarizer(text: str, max_sentences: int = 3) -> dict:
    summary = gemini_service.summarize(text, max_sentences=max_sentences)
    return {"summary": summary, "original_length": len(text)}


def keyword_extractor(text: str, top_n: int = 10) -> dict:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    stop = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
        "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
        "how", "its", "may", "new", "now", "old", "see", "two", "way", "who",
        "with", "this", "that", "from", "have", "will", "your", "what", "when",
    }
    freq: dict[str, int] = {}
    for w in words:
        if w not in stop:
            freq[w] = freq.get(w, 0) + 1
    sorted_kw = sorted(freq.items(), key=lambda x: -x[1])[:top_n]
    return {"keywords": [{"word": k, "count": v} for k, v in sorted_kw]}


def json_formatter(text: str) -> dict:
    try:
        parsed = json.loads(text)
        return {"valid": True, "formatted": json.dumps(parsed, indent=2)}
    except json.JSONDecodeError as exc:
        return {"valid": False, "error": str(exc)}


def text_cleaner(text: str) -> dict:
    cleaned = re.sub(r"\s+", " ", text).strip()
    cleaned = re.sub(r"[^\w\s.,!?@#%&*()\-:/]", "", cleaned)
    return {"original_length": len(text), "cleaned": cleaned, "cleaned_length": len(cleaned)}


def job_filter(jobs: list[dict], keyword: str) -> dict:
    kw = keyword.lower()
    filtered = [
        j
        for j in jobs
        if kw in (j.get("title", "") + j.get("company", "") + j.get("description", "")).lower()
    ]
    return {"keyword": keyword, "count": len(filtered), "jobs": filtered}


def search_optimizer(query: str) -> dict:
    """Suggest optimized job search query."""
    base = query.strip().lower()
    extras = []
    if "ai" not in base:
        extras.append("AI OR machine learning")
    if "remote" not in base:
        extras.append("remote")
    optimized = f"{query} {' '.join(extras)}".strip()
    return {"original": query, "optimized": optimized}


FUNCTION_REGISTRY = {
    "calculator": calculator,
    "datetime_tool": datetime_tool,
    "url_extractor": url_extractor,
    "text_summarizer": text_summarizer,
    "keyword_extractor": keyword_extractor,
    "json_formatter": json_formatter,
    "text_cleaner": text_cleaner,
    "job_filter": job_filter,
    "search_optimizer": search_optimizer,
}


TOOL_DECLARATIONS = [
    {
        "name": "search_jobs",
        "description": "Search for AI, automation, Python, React, full-stack, and remote developer jobs",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Job search keywords"},
                "limit": {"type": "integer", "description": "Max results, default 10"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "save_note",
        "description": "Save a note with title and content",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "content"],
        },
    },
    {
        "name": "list_notes",
        "description": "List all saved notes",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "send_email",
        "description": "Send an email to a recipient",
        "parameters": {
            "type": "object",
            "properties": {
                "to_email": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to_email", "subject", "body"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluate a math expression",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
    {
        "name": "datetime_tool",
        "description": "Get current date and time",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "url_extractor",
        "description": "Extract URLs from text",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "text_summarizer",
        "description": "Summarize long text",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "keyword_extractor",
        "description": "Extract keywords from text",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
]
