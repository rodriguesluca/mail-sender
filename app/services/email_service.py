import smtplib
import base64
from email.message import EmailMessage
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def send_email_sync(
    to_email: str | list,
    cc_email: str | list | None,
    subject: str,
    body: str,
    smtp_user: str,
    smtp_password: str,
    smtp_host: str,
    smtp_port: int,
    smtp_tls: bool,
    attachment_base64: str | None = None,
    attachment_filename: str | None = None,
) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user

    if isinstance(to_email, list):
        msg["To"] = ", ".join(to_email)
    else:
        msg["To"] = to_email

    if cc_email:
        if isinstance(cc_email, list):
            msg["Cc"] = ", ".join(cc_email)
        else:
            msg["Cc"] = cc_email

    msg.set_content(body)

    if attachment_base64 and attachment_filename:
        try:
            file_data = base64.b64decode(attachment_base64)
            # You might want to infer maintype and subtype based on filename extension
            # For simplicity, we use application/octet-stream as default for unknown types
            msg.add_attachment(
                file_data,
                maintype="application",
                subtype="octet-stream",
                filename=attachment_filename,
            )
        except Exception as e:
            logger.error(f"Failed to decode attachment: {e}")
            raise ValueError("Invalid Base64 attachment") from e

    try:
        with smtplib.SMTP(smtp_host.strip(), smtp_port) as server:
            if smtp_tls:
                server.starttls()
            server.login(smtp_user.strip(), smtp_password.strip())
            server.send_message(msg)
            logger.info(f"Email sent successfully to {to_email} from {smtp_user}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise
