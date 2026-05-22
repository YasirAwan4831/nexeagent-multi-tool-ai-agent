"""Input validation helpers."""

import re


EMAIL_REGEX = re.compile(r"^[\w.\-+]+@[\w.\-]+\.\w+$")


def validate_email(email: str) -> tuple[bool, str]:
    if not email or not email.strip():
        return False, "Email is required"
    if not EMAIL_REGEX.match(email.strip()):
        return False, "Invalid email format"
    return True, ""


def validate_required(value: str, field: str) -> tuple[bool, str]:
    if not value or not str(value).strip():
        return False, f"{field} is required"
    return True, ""


def validate_note(note: dict) -> tuple[bool, str]:
    if not isinstance(note, dict):
        return False, "Invalid note payload"
    ok, msg = validate_required(note.get("title", ""), "Title")
    if not ok:
        return ok, msg
    ok, msg = validate_required(note.get("content", ""), "Content")
    return ok, msg
