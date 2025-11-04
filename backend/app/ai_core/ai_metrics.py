"""
Geko AI Core - AI Metrics & Logging
Sistema di monitoraggio, logging e diagnostica per l'AI Core
"""

import psutil
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None


class AIMetrics:
    """
    Classe per raccolta, logging e diagnostica delle metriche AI.
    
    Fornisce:
    - Raccolta metriche sistema (CPU, RAM, GPU)
    - Logging strutturato eventi AI
    - Formattazione JSON per compatibilità dashboard
    """
    
    @staticmethod
    def collect_metrics() -> Dict[str, Any]:
        """
        Raccoglie metriche di sistema (CPU, RAM, GPU).
        
        Returns:
            Dict con metriche sistema
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": round(cpu_percent, 2),
                "cpu_count": psutil.cpu_count(),
                "ram_total_gb": round(memory.total / (1024**3), 2),
                "ram_used_gb": round(memory.used / (1024**3), 2),
                "ram_available_gb": round(memory.available / (1024**3), 2),
                "ram_percent": round(memory.percent, 2),
            }
            
            # GPU info se disponibile
            if TORCH_AVAILABLE and torch.cuda.is_available():
                try:
                    gpu_count = torch.cuda.device_count()
                    gpu_name = torch.cuda.get_device_name(0)
                    
                    # GPU memory
                    if hasattr(torch.cuda, 'get_device_properties'):
                        props = torch.cuda.get_device_properties(0)
                        gpu_memory_total = props.total_memory / (1024**3)
                    else:
                        gpu_memory_total = None
                    
                    metrics.update({
                        "gpu_available": True,
                        "gpu_count": gpu_count,
                        "gpu_name": gpu_name,
                        "gpu_memory_total_gb": round(gpu_memory_total, 2) if gpu_memory_total else None,
                    })
                except Exception as e:
                    metrics.update({
                        "gpu_available": False,
                        "gpu_error": str(e)
                    })
            else:
                metrics.update({
                    "gpu_available": False,
                    "gpu_name": None
                })
            
            return metrics
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": f"Errore raccolta metriche: {str(e)}"
            }
    
    @staticmethod
    def log_inference(
        model_name: str,
        elapsed_ms: float,
        success: bool = True,
        error: Optional[Exception] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea entry di log per evento inferenza.
        
        Args:
            model_name: Nome modello utilizzato
            elapsed_ms: Tempo inferenza in millisecondi
            success: Se True, inferenza riuscita
            error: Eccezione se inferenza fallita
            additional_data: Dati aggiuntivi da includere
            
        Returns:
            Dict con log entry completo
        """
        metrics = AIMetrics.collect_metrics()
        
        log_entry = {
            "event": "inference",
            "model": model_name,
            "elapsed_ms": round(elapsed_ms, 2),
            "success": success,
            "error": str(error) if error else None,
            **metrics
        }
        
        if additional_data:
            log_entry.update(additional_data)
        
        return log_entry
    
    @staticmethod
    def log_preprocessing(
        text_length: int,
        token_count: int,
        processing_time_ms: float,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crea entry di log per pre-processing.
        
        Args:
            text_length: Lunghezza testo originale
            token_count: Numero tokens generati
            processing_time_ms: Tempo pre-processing in ms
            model_name: Nome modello (opzionale)
            
        Returns:
            Dict con log entry
        """
        metrics = AIMetrics.collect_metrics()
        
        log_entry = {
            "event": "preprocessing",
            "text_length": text_length,
            "token_count": token_count,
            "processing_time_ms": round(processing_time_ms, 2),
            **metrics
        }
        
        if model_name:
            log_entry["model"] = model_name
        
        return log_entry
    
    @staticmethod
    def log_model_loading(
        model_name: str,
        load_time_ms: float,
        success: bool = True,
        source: Optional[str] = None,
        error: Optional[Exception] = None
    ) -> Dict[str, Any]:
        """
        Crea entry di log per caricamento modello.
        
        Args:
            model_name: Nome modello
            load_time_ms: Tempo caricamento in ms
            success: Se True, caricamento riuscito
            source: Sorgente modello (cache, hub, local)
            error: Eccezione se caricamento fallito
            
        Returns:
            Dict con log entry
        """
        metrics = AIMetrics.collect_metrics()
        
        log_entry = {
            "event": "model_loading",
            "model": model_name,
            "load_time_ms": round(load_time_ms, 2),
            "success": success,
            "source": source,
            "error": str(error) if error else None,
            **metrics
        }
        
        return log_entry
    
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        """
        Restituisce stato di salute del sistema AI.
        
        Returns:
            Dict con health status
        """
        metrics = AIMetrics.collect_metrics()
        
        # Valuta health status
        health_status = "healthy"
        warnings = []
        
        # CPU check
        if metrics.get("cpu_percent", 0) > 90:
            health_status = "warning"
            warnings.append("CPU usage > 90%")
        
        # RAM check
        if metrics.get("ram_percent", 0) > 90:
            health_status = "warning"
            warnings.append("RAM usage > 90%")
        
        # GPU check
        if metrics.get("gpu_available") and TORCH_AVAILABLE:
            try:
                if torch.cuda.memory_allocated(0) / torch.cuda.max_memory_allocated(0) > 0.9:
                    warnings.append("GPU memory usage > 90%")
            except:
                pass
        
        return {
            "status": health_status,
            "warnings": warnings,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }


def format_log_entry(log_entry: Dict[str, Any]) -> str:
    """
    Formatta log entry come JSON string.
    
    Args:
        log_entry: Dict con dati log
        
    Returns:
        JSON string formattato
    """
    return json.dumps(log_entry, ensure_ascii=False, indent=None)

