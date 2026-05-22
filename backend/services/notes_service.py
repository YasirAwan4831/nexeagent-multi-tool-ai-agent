"""Notes CRUD backed by notes.json."""

from config import NOTES_FILE
from utils.helpers import generate_id, utc_now_iso
from utils.json_db import JsonDatabase
from utils.logger import log_event


class NotesService:
    def __init__(self):
        self.db = JsonDatabase(NOTES_FILE, default=[])

    def list_notes(self, tag: str | None = None) -> list[dict]:
        notes = self.db.read()
        if tag:
            notes = [n for n in notes if tag.lower() in (n.get("tags") or [])]
        return sorted(notes, key=lambda x: x.get("updated_at", ""), reverse=True)

    def get_note(self, note_id: str) -> dict | None:
        return next((n for n in self.db.read() if n.get("id") == note_id), None)

    def create_note(
        self,
        title: str,
        content: str,
        tags: list[str] | None = None,
        note_type: str = "user",
    ) -> dict:
        note = {
            "id": generate_id("note"),
            "title": title.strip(),
            "content": content.strip(),
            "tags": tags or [],
            "type": note_type,
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
        }
        notes = self.db.read()
        notes.append(note)
        self.db.write(notes)
        log_event("info", f"Note created: {note['id']}")
        return note

    def update_note(self, note_id: str, data: dict) -> dict | None:
        notes = self.db.read()
        for i, note in enumerate(notes):
            if note.get("id") == note_id:
                if "title" in data:
                    note["title"] = data["title"].strip()
                if "content" in data:
                    note["content"] = data["content"].strip()
                if "tags" in data:
                    note["tags"] = data["tags"]
                note["updated_at"] = utc_now_iso()
                notes[i] = note
                self.db.write(notes)
                log_event("info", f"Note updated: {note_id}")
                return note
        return None

    def delete_note(self, note_id: str) -> bool:
        notes = self.db.read()
        new_notes = [n for n in notes if n.get("id") != note_id]
        if len(new_notes) == len(notes):
            return False
        self.db.write(new_notes)
        log_event("info", f"Note deleted: {note_id}")
        return True


notes_service = NotesService()
