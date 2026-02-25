import logging
from cryptography.fernet import Fernet, InvalidToken
from app.core.config import settings

logger = logging.getLogger(__name__)


def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypts an encrypted SMTP password using the global ENCRYPTION_KEY.
    """
    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY is not configured in the environment.")

    try:
        clean_key = settings.ENCRYPTION_KEY.strip("'\"")
        fernet = Fernet(clean_key.encode("utf-8"))
        decrypted_bytes = fernet.decrypt(encrypted_password.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except InvalidToken:
        logger.error(
            "Failed to decrypt password: Invalid token or encryption key mismatch."
        )
        raise ValueError("Invalid encrypted password provided.")
    except Exception as e:
        logger.error(f"Unexpected error during decryption: {e}")
        raise ValueError("Failed to decrypt password.")


def encrypt_raw_password(raw_password: str) -> str:
    """
    Encrypts a plaintext SMTP password using the global ENCRYPTION_KEY.
    Useful for the frontend utility generator.
    """
    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY is not configured in the environment.")

    clean_key = settings.ENCRYPTION_KEY.strip("'\"")
    fernet = Fernet(clean_key.encode("utf-8"))
    encrypted_bytes = fernet.encrypt(raw_password.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")
