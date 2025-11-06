from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings
from typing import List, Union


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str

    # App Environment
    ENVIRONMENT: str = "development"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()