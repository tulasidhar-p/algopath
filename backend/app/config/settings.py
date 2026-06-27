"""Centralized configuration settings for the AlgoPath application.

This module loads environment variables from a .env file and exposes them as
typed configurations for the database, security parameters, and CORS configurations.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings class container."""

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./algopath.db")

    # Security settings for JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_IN_DEVELOPMENT")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # CORS settings
    CORS_ALLOWED_ORIGINS: str = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )


# Globally accessible configuration settings instance
settings = Settings()
