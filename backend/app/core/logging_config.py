"""Configurazione logging per il backend Geko."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_FILE = LOG_DIR / "backend.log"


def setup_logging(level: Optional[int] = None) -> None:
    """
    Configura logging centralizzato per il backend.

    Se già configurato, rimuove gli handler precedenti per evitare duplicazioni.
    """

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    while root_logger.handlers:
        handler = root_logger.handlers.pop()
        handler.close()

    logging.basicConfig(
        level=level or logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    logging.getLogger(__name__).info("Logging initialized for Geko Backend")

