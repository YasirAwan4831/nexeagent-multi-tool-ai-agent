"""Notes tool wrapper for agent execution."""

from services.notes_service import notes_service


def save_note(title: str, content: str, tags: list | None = None) -> dict:
    note = notes_service.create_note(title, content, tags=tags)
    return {"success": True, "note": note}


def list_notes() -> dict:
    notes = notes_service.list_notes()
    return {"count": len(notes), "notes": notes}
