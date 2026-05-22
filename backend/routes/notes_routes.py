"""Notes API routes."""

from flask import Blueprint, jsonify, request

from services.notes_service import notes_service
from utils.validators import validate_note

notes_bp = Blueprint("notes", __name__, url_prefix="/api/notes")


@notes_bp.route("", methods=["GET"])
def list_notes():
    tag = request.args.get("tag")
    notes = notes_service.list_notes(tag=tag)
    return jsonify({"success": True, "notes": notes, "count": len(notes)})


@notes_bp.route("/<note_id>", methods=["GET"])
def get_note(note_id):
    note = notes_service.get_note(note_id)
    if not note:
        return jsonify({"success": False, "error": "Note not found"}), 404
    return jsonify({"success": True, "note": note})


@notes_bp.route("", methods=["POST"])
def create_note():
    data = request.get_json(silent=True) or {}
    ok, err = validate_note(data)
    if not ok:
        return jsonify({"success": False, "error": err}), 400
    note = notes_service.create_note(
        data["title"],
        data["content"],
        tags=data.get("tags"),
        note_type=data.get("type", "user"),
    )
    return jsonify({"success": True, "note": note}), 201


@notes_bp.route("/<note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json(silent=True) or {}
    note = notes_service.update_note(note_id, data)
    if not note:
        return jsonify({"success": False, "error": "Note not found"}), 404
    return jsonify({"success": True, "note": note})


@notes_bp.route("/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    deleted = notes_service.delete_note(note_id)
    if not deleted:
        return jsonify({"success": False, "error": "Note not found"}), 404
    return jsonify({"success": True, "message": "Note deleted"})
