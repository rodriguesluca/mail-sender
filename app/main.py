from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.schemas import EmailRequest, EncryptRequest
from app.worker import send_email_task
from app.core.security import encrypt_raw_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MailSender Service",
    description="Microservice for sending emails asynchronously via Celery.",
)

# Mount the static directory to serve CSS and JS
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.post(
    "/send-email/",
    status_code=202,
    responses={
        202: {
            "description": "Email request queued successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Email request queued successfully.",
                        "task_id": "b0682121-6577-4c3d-abfc-f8b8a5fc425f",
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error while queueing email."}
                }
            },
        },
    },
)
def schedule_email(request: EmailRequest):
    """
    Endpoint to receive email details and schedule them for sending.
    Returns 202 Accepted if the task was queued successfully.
    """
    try:
        task = send_email_task.delay(request.model_dump())
        logger.info(f"Queued email task {task.id} for {request.to_email}")
        return {"message": "Email request queued successfully.", "task_id": task.id}
    except Exception as e:
        logger.error(f"Failed to queue email task: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while queueing email."
        )


@app.post("/encrypt/")
def encrypt_password_endpoint(request: EncryptRequest):
    """
    Encrypts a raw SMTP password into a Fernet token for the frontend utility.
    """
    try:
        token = encrypt_raw_password(request.raw_password)
        return {"encrypted_token": token}
    except Exception as e:
        logger.error(f"Failed to encrypt password: {e}")
        raise HTTPException(status_code=500, detail="Failed to encrypt password.")


@app.get("/")
def serve_frontend():
    """
    Serves the beautiful Vue/Vanilla JS frontend interface to test email dispatch.
    """
    return FileResponse("app/static/index.html")
