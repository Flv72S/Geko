"""
Geko AI Core - AI Logger
Sistema di logging strutturato con rotazione automatica per AI Core
"""

import logging
import json
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class JSONFormatter(logging.Formatter):
    """Formatter che formatta log come JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatta record come JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Aggiungi dati extra se presenti
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        # Aggiungi exception info se presente
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_ai_logger(log_file: str = "ai_metrics.log", max_bytes: int = 5 * 1024 * 1024, backup_count: int = 5) -> logging.Logger:
    """
    Configura logger AI con rotazione automatica.
    
    Args:
        log_file: Nome file log
        max_bytes: Dimensione massima file (default 5MB)
        backup_count: Numero file backup da mantenere
        
    Returns:
        Logger configurato
    """
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_path = log_dir / log_file
    
    # Crea logger
    logger = logging.getLogger("geko.ai_core")
    logger.setLevel(logging.INFO)
    
    # Rimuovi handlers esistenti per evitare duplicati
    logger.handlers.clear()
    
    # Handler file con rotazione
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    
    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Logger globale
ai_logger = setup_ai_logger()


def log_ai_event(logger: logging.Logger, event_type: str, data: Dict[str, Any], level: str = "info"):
    """
    Logga evento AI con dati strutturati.
    
    Args:
        logger: Logger instance
        event_type: Tipo evento (es. "inference", "preprocessing")
        data: Dati da loggare
        level: Livello log (debug, info, warning, error)
    """
    log_method = getattr(logger, level.lower(), logger.info)
    
    # Crea record con extra_data
    extra = {"extra_data": {"event_type": event_type, **data}}
    log_method(f"[{event_type}] {data.get('message', '')}", extra=extra)

