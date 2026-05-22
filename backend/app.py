"""
NEXEAGENT Multi-Tool AI Agent — Flask Application Entry Point

Run from project root or backend directory:
    python backend/app.py
    python app.py   (when cwd is backend/)

Configure GEMINI_API_KEY and SMTP credentials in backend/.env
"""

import os
import sys
from pathlib import Path

# Ensure imports and .env resolve regardless of launch directory
_BACKEND_DIR = Path(__file__).resolve().parent
os.chdir(_BACKEND_DIR)
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from flask import Flask, jsonify
from flask_cors import CORS

from config import CORS_ORIGINS, DATABASE_DIR, FLASK_DEBUG, FLASK_HOST, FLASK_PORT
from routes.chat_routes import chat_bp
from routes.email_routes import email_bp
from routes.jobs_routes import jobs_bp
from routes.notes_routes import notes_bp
from routes.tools_routes import tools_bp
from utils.logger import log_event, setup_logger

setup_logger()


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins=CORS_ORIGINS, supports_credentials=True)

    app.register_blueprint(chat_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(tools_bp)

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    @app.route("/", methods=["GET"])
    def index():
        return "Backend is running"

    @app.route("/api/health", methods=["GET"])
    def health():
        from services.gemini_service import gemini_service
        from services.email_service import email_service

        return jsonify({
            "status": "ok",
            "service": "NEXEAGENT Multi-Tool AI Agent",
            "gemini_configured": gemini_service.is_available,
            "gemini_model": getattr(gemini_service, "active_model", None),
            "email_configured": email_service.is_configured,
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        log_event("error", str(e))
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    log_event("info", f"Starting NEXEAGENT on {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
