"""
Geko AI Core - Modulo principale
Gestisce la logica centrale dell'AI Core
"""

from .ai_metrics import AIMetrics
from .ai_logger import ai_logger, log_ai_event
from .ai_validation import AICoreValidator, AIFallbackManager


class GekoAICore:
    """Classe principale per Geko AI Core"""
    
    def __init__(self):
        self.status = "initialized"
        self.model_loaded = False
        self.validator = AICoreValidator()
        self.fallback_manager = AIFallbackManager()
        
        # Log inizializzazione
        log_entry = AIMetrics.collect_metrics()
        log_entry.update({
            "event": "ai_core_initialized",
            "status": self.status
        })
        log_ai_event(ai_logger, "initialization", log_entry, "info")
    
    def analyze(self, input_data: str):
        """
        Analizza input data e restituisce risultati
        """
        return {
            "input": input_data,
            "output": "mock_response",
            "status": self.status,
            "model_loaded": self.model_loaded,
            "validation_threshold": self.validator.default_threshold,
            "fallback_models": self.fallback_manager.list_models()
        }
    
    def get_status(self):
        """Restituisce lo status corrente del sistema"""
        return {
            "status": self.status,
            "model_loaded": self.model_loaded,
            "validation_threshold": self.validator.default_threshold,
            "fallback_models": self.fallback_manager.list_models()
        }

