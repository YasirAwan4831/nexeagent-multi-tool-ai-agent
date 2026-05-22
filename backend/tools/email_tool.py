"""Email tool wrapper for agent execution."""

from services.email_service import email_service


def send_email(to_email: str, subject: str, body: str) -> dict:
    return email_service.send_email(to_email, subject, body)
