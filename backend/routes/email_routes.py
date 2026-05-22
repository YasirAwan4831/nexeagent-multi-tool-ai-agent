"""Email API routes."""

from flask import Blueprint, jsonify, request

from services.email_service import email_service
from utils.validators import validate_email, validate_required

email_bp = Blueprint("email", __name__, url_prefix="/api/email")


@email_bp.route("/send", methods=["POST"])
def send_email():
    data = request.get_json(silent=True) or {}
    to_email = data.get("to", data.get("to_email", ""))
    subject = data.get("subject", "")
    body = data.get("body", "")

    ok, err = validate_email(to_email)
    if not ok:
        return jsonify({"success": False, "error": err}), 400
    ok, err = validate_required(subject, "Subject")
    if not ok:
        return jsonify({"success": False, "error": err}), 400
    ok, err = validate_required(body, "Body")
    if not ok:
        return jsonify({"success": False, "error": err}), 400

    result = email_service.send_email(to_email, subject, body)
    status = 200 if result.get("success") else 503
    return jsonify(result), status


@email_bp.route("/status", methods=["GET"])
def email_status():
    return jsonify({
        "configured": email_service.is_configured,
        "message": (
            "Email ready"
            if email_service.is_configured
            else "Configure SMTP_USER and SMTP_PASSWORD in backend/.env"
        ),
    })
