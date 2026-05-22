"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Gemini API — set GEMINI_API_KEY in backend/.env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()

# Flask
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "nexeagent-dev-secret-change-in-production")

# CORS
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if o.strip()
]

# Email (Gmail SMTP) — set in backend/.env; never commit real credentials
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
# Gmail app passwords are often copied with spaces — remove them
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").replace(" ", "").strip()
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER).strip() or SMTP_USER
DEFAULT_EMAIL_TO = os.getenv("DEFAULT_EMAIL_TO", "").strip()

# Database paths
DATABASE_DIR = BASE_DIR / "database"
NOTES_FILE = DATABASE_DIR / "notes.json"
JOBS_FILE = DATABASE_DIR / "jobs.json"
LOGS_FILE = DATABASE_DIR / "logs.json"
CHAT_HISTORY_FILE = DATABASE_DIR / "chat_history.json"

PROMPTS_DIR = BASE_DIR / "prompts"
SYSTEM_PROMPT_FILE = PROMPTS_DIR / "system_prompt.txt"
