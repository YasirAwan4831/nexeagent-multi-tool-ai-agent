"""Chat and agent API routes."""

from flask import Blueprint, jsonify, request

from services.agent_service import agent_service
from utils.validators import validate_required

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@chat_bp.route("/message", methods=["POST"])
def send_message():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    ok, err = validate_required(message, "Message")
    if not ok:
        return jsonify({"success": False, "error": err}), 400

    session_id = data.get("session_id", "default")
    result = agent_service.process_message(message, session_id=session_id)
    return jsonify({"success": True, **result})


@chat_bp.route("/history", methods=["GET"])
def get_history():
    session_id = request.args.get("session_id", "default")
    history = agent_service.get_history(session_id)
    return jsonify({"success": True, "history": history, "session_id": session_id})


@chat_bp.route("/sessions", methods=["GET"])
def list_sessions():
    sessions = agent_service.list_sessions()
    return jsonify({"success": True, "sessions": sessions})
