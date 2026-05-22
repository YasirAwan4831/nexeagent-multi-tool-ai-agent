"""Shared helper utilities."""

import re
import uuid
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_id(prefix: str = "id") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def extract_urls(text: str) -> list[str]:
    pattern = r"https?://[^\s<>\"']+"
    return list(dict.fromkeys(re.findall(pattern, text)))


def extract_company_from_title(title: str) -> str:
    """Heuristic: 'Role at Company' or 'Company - Role'."""
    if " at " in title.lower():
        parts = re.split(r"\s+at\s+", title, flags=re.IGNORECASE, maxsplit=1)
        if len(parts) == 2:
            return parts[1].strip()
    if " - " in title:
        return title.split(" - ", 1)[0].strip()
    return "Unknown"


def truncate(text: str, max_len: int = 200) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
