from celery import Celery
from app.core.config import settings
from app.services.email_service import send_email_sync
from app.core.security import decrypt_password
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    "mail_worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="send_email_task", bind=True, max_retries=3)
def send_email_task(self, email_data: dict):
    """
    Celery task to send an email in the background.
    """
    try:
        logger.info(f"Starting email task for {email_data.get('to_email')}")

        # Decrypt the received password
        raw_password = email_data.get("smtp_password")
        decrypted_password = decrypt_password(raw_password)

        send_email_sync(
            to_email=email_data.get("to_email"),
            cc_email=email_data.get("cc_email"),
            subject=email_data.get("subject"),
            body=email_data.get("body"),
            smtp_user=email_data.get("smtp_user"),
            smtp_password=decrypted_password,
            smtp_host=email_data.get("smtp_host", "smtp.office365.com"),
            smtp_port=email_data.get("smtp_port", 587),
            smtp_tls=email_data.get("smtp_tls", True),
            attachment_base64=email_data.get("attachment_base64"),
            attachment_filename=email_data.get("attachment_filename"),
        )
        return {
            "status": "success",
            "message": f"Email sent to {email_data.get('to_email')}",
        }
    except Exception as exc:
        logger.error(f"Error sending email: {exc}")
        raise self.retry(exc=exc, countdown=15)  # Retry after 15 seconds
