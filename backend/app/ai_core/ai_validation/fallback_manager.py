"""
Gestione fallback per Geko AI Core
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import logging
from logging.handlers import RotatingFileHandler

from ..model_loader import ModelLoader


def _setup_fallback_logger() -> logging.Logger:
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "ai_fallback.log"
    logger = logging.getLogger("geko.ai_core.fallback")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


fallback_logger = _setup_fallback_logger()


class AIFallbackManager:
    """Gestisce fallback e modelli alternativi per AI Core."""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.registry: Dict[str, Dict[str, Any]] = {}
        self.primary_model: Optional[str] = None

    def register_model(self, name: str, path: Optional[str] = None, priority: int = 1):
        self.registry[name] = {
            "path": path or name,
            "priority": priority,
            "last_used": None,
        }
        if self.primary_model is None or priority < self.registry[self.primary_model]["priority"]:
            self.primary_model = name
        fallback_logger.info(json.dumps({"event": "register_model", "model": name, "priority": priority}))

    def get_fallback_model(self, current_model: str) -> Optional[Dict[str, Any]]:
        candidates = [
            {"name": name, **info}
            for name, info in self.registry.items()
            if name != current_model
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda x: x.get("priority", 1))
        fallback_logger.info(json.dumps({"event": "get_fallback_model", "current": current_model, "fallback": candidates[0]["name"]}))
        return candidates[0]

    def handle_failure(self, event: Dict[str, Any]) -> Dict[str, Any]:
        current_model = event.get("model")
        reason = event.get("reason", "unknown")
        fallback = self.get_fallback_model(current_model)
        if not fallback:
            response = {
                "action": "no_fallback_available",
                "model_used": current_model,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
            }
            self.log_fallback(response)
            return response

        response = {
            "action": "switch_model",
            "model_used": fallback["name"],
            "reason": reason,
            "target_path": fallback["path"],
            "timestamp": datetime.now().isoformat(),
        }
        self.log_fallback(response)
        return response

    def log_fallback(self, event: Dict[str, Any], level: str = "info"):
        data = {"event": "fallback", **event}
        getattr(fallback_logger, level)(json.dumps(data))

    def list_models(self):
        return [
            {
                "name": name,
                "path": data.get("path"),
                "priority": data.get("priority"),
                "last_used": data.get("last_used")
            }
            for name, data in sorted(self.registry.items(), key=lambda item: item[1].get("priority", 1))
        ]

    def load_model(self, model_identifier: str, **loader_kwargs) -> Dict[str, Any]:
        loader = ModelLoader(model_name=model_identifier, device=self.device, **loader_kwargs)
        bundle = loader.load_model()
        fallback_logger.info(json.dumps({"event": "fallback_model_loaded", "model": model_identifier, "source": bundle.get("source")}))
        return {"bundle": bundle, "loader": loader}
