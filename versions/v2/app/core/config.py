from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "openEMIS v2"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql://openemis:openemis@localhost:5432/openemis_v2"

    SECRET_KEY: str = "openemis-v2-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8001",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
