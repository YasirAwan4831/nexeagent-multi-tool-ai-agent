"""Email automation via Gmail SMTP — configure SMTP_* in backend/.env"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER
from utils.logger import log_event


class EmailService:
    @property
    def is_configured(self) -> bool:
        return bool(SMTP_USER and SMTP_PASSWORD and EMAIL_FROM)

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> dict:
        if not self.is_configured:
            return {
                "success": False,
                "message": (
                    "Email not configured. Set SMTP_USER, SMTP_PASSWORD, and EMAIL_FROM "
                    "in backend/.env (use a Gmail app password)."
                ),
            }

        to_email = (to_email or "").strip()
        if not to_email:
            return {"success": False, "message": "Recipient email is required"}

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = EMAIL_FROM
            msg["To"] = to_email

            subtype = "html" if html else "plain"
            msg.attach(MIMEText(body, subtype, "utf-8"))

            context = ssl.create_default_context()
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(EMAIL_FROM, [to_email], msg.as_string())

            log_event("info", f"Email sent to {to_email}", {"subject": subject})
            return {"success": True, "message": f"Email sent successfully to {to_email}"}
        except smtplib.SMTPAuthenticationError as exc:
            log_event("error", f"SMTP auth failed: {exc}")
            return {
                "success": False,
                "message": (
                    "Gmail authentication failed. Use an App Password (not your login password) "
                    "for SMTP_PASSWORD and ensure 2-Step Verification is enabled."
                ),
            }
        except Exception as exc:
            log_event("error", f"Email failed: {exc}")
            return {"success": False, "message": str(exc)}


email_service = EmailService()
