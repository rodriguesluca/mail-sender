from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000

    REDIS_URL: str = "redis://redis:6379/0"

    # Needs to be a valid 32-url-safe-base64-encoded string for Fernet
    ENCRYPTION_KEY: str

    SMTP_SERVER: str
    SMTP_PORT: int

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
