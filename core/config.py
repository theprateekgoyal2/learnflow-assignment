"""Application configuration loaded from environment variables."""

import os


class Config:
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    DB_PATH: str = os.getenv("DB_PATH", "learnflow.db")


config = Config()
