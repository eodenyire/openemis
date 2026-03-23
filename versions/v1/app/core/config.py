from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "CBC EMIS Kenya"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://openemis:openemis@localhost:5432/openemis_db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # M-Pesa Daraja API
    MPESA_CONSUMER_KEY: str = ""
    MPESA_CONSUMER_SECRET: str = ""
    MPESA_SHORTCODE: str = ""
    MPESA_PASSKEY: str = ""
    MPESA_CALLBACK_URL: str = "https://yourdomain.com/api/v1/payments/mpesa/callback"
    MPESA_BASE_URL: str = "https://sandbox.safaricom.co.ke"  # switches to prod via env

    @property
    def mpesa_base_url(self) -> str:
        if self.MPESA_ENV == "production":
            return "https://api.safaricom.co.ke"
        return "https://sandbox.safaricom.co.ke"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Africa's Talking SMS
    AT_API_KEY: str = ""
    AT_USERNAME: str = "sandbox"
    AT_SENDER_ID: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
