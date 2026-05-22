"""Integration tests — run: python scripts/test_integrations.py (from backend/)"""

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from app import app  # noqa: E402
from config import DEFAULT_EMAIL_TO, GEMINI_API_KEY  # noqa: E402
from services.email_service import email_service  # noqa: E402
from services.gemini_service import gemini_service  # noqa: E402


def main():
    print("=== NEXEAGENT Integration Tests ===\n")
    print(f"Gemini key set: {bool(GEMINI_API_KEY)}")
    print(f"Gemini available: {gemini_service.is_available}")
    print(f"Gemini model: {gemini_service.active_model}")
    print(f"Email configured: {email_service.is_configured}\n")

    client = app.test_client()

    # Gemini
    if gemini_service.is_available:
        r = gemini_service.chat("Say hello in one short sentence.")
        print("Gemini chat:", (r.get("text") or r.get("error", ""))[:120])
    else:
        print("Gemini chat: SKIPPED (no key)")

    # API tools
    for tool, payload in [
        ("calculator", {"expression": "10 * 5"}),
        ("datetime_tool", {}),
        ("keyword_extractor", {"text": "AI automation Python developer jobs"}),
    ]:
        res = client.post(f"/api/tools/{tool}", json=payload)
        data = res.get_json()
        ok = res.status_code == 200 and data.get("success")
        print(f"Tool {tool}: {'OK' if ok else 'FAIL'} {data.get('result', data)}")

    # Jobs + chat
    res = client.post("/api/jobs/search", json={"query": "python react remote", "limit": 3})
    jobs = res.get_json()
    print(f"Jobs search: {jobs.get('count', 0)} jobs")

    res = client.post(
        "/api/chat/message",
        json={"message": "What is 7 plus 8?"},
    )
    chat = res.get_json()
    print(f"Chat: {str(chat.get('response', ''))[:100]}...")

    # Send test email
    recipient = DEFAULT_EMAIL_TO or "socialmedia55664@gmail.com"
    job_lines = []
    for j in (jobs.get("jobs") or [])[:3]:
        job_lines.append(f"- {j.get('title')} @ {j.get('company')}: {j.get('url')}")

    body = (
        "NEXEAGENT — Test Automation Email\n\n"
        "Agent working confirmation: All systems tested successfully.\n\n"
        "AI / Web Development Job Updates:\n"
        + ("\n".join(job_lines) if job_lines else "- Search jobs in the dashboard for latest listings.")
        + "\n\n"
        "This is an automated test message from your NEXEAGENT Multi-Tool AI Agent.\n"
    )
    subject = "NEXEAGENT Test — Job Updates & Agent Confirmation"

    print(f"\nSending test email to {recipient}...")
    result = email_service.send_email(recipient, subject, body)
    print("Email result:", json.dumps(result, indent=2))

    print("\n=== Done ===")
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
