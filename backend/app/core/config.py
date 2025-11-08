"""Configurazione centrale del backend Geko."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Impostazioni applicative caricate da variabili d'ambiente."""

    APP_NAME: str = "Geko Backend"
    APP_PORT: int = 8000
    ENV: str = "development"
    DATABASE_URL: Optional[str] = None

    class Config:
        env_file = str(Path(__file__).resolve().parents[3] / ".env")
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()