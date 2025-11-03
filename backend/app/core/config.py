from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = str(Path(__file__).parent.parent.parent.parent / ".env")
        extra = "ignore"  # Ignora variabili extra nel .env


settings = Settings()

