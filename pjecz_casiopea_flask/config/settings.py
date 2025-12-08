"""
Settings
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()
SERVICE_PREFIX = os.getenv("SERVICE_PREFIX", "pjecz_casiopea_flask")


class Settings(BaseSettings):
    """Settings"""

    # Variables de entorno
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    FERNET_KEY: str = os.getenv("FERNET_KEY", "")
    HOST: str = os.getenv("HOST", "")
    PREFIX: str = os.getenv("PREFIX", "")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "6379")
    SALT: str = os.getenv("SALT", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    SQLALCHEMY_DATABASE_URI: str = os.getenv("SQLALCHEMY_DATABASE_URI", "")
    TASK_QUEUE_NAME: str = os.getenv("TASK_QUEUE_NAME", "pjecz_casiopea")
    TZ: str = os.getenv("TZ", "America/Mexico_City")

    # Incrementar el tamaño de lo que se sube en los formularios
    MAX_CONTENT_LENGTH: int | None = None
    MAX_FORM_MEMORY_SIZE: int = 50 * (2**10) ** 2  # 50 MB

    class Config:
        """Load configuration"""

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            """Change the order of precedence of settings sources"""
            return env_settings, file_secret_settings, init_settings


@lru_cache()
def get_settings() -> Settings:
    """Get Settings"""
    return Settings()
