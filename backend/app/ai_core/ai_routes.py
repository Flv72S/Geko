"""
Geko AI Core - API Routes
Endpoint FastAPI per l'AI Core
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .pipeline_manager import PipelineManager, run_pipeline
from .core_ai import GekoAICore

router = APIRouter(prefix="/ai", tags=["AI Core"])

# Istanza globale AI Core
ai_core = GekoAICore()

# PipelineManager globale (inizializzato lazy)
_pipeline_manager = None


class AnalyzeRequest(BaseModel):
    """Modello per richiesta analisi"""
    text: str
    options: Optional[dict] = None


@router.get("/test")
def test_ai():
    """
    Endpoint di test per verificare che AI Core sia connesso
    
    Returns:
        Status del sistema AI Core
    """
    status = ai_core.get_status()
    return {
        "status": "AI Core connected",
        "ai_core_status": status
    }


@router.post("/analyze")
def analyze_text(data: AnalyzeRequest):
    """
    Endpoint per analizzare testo usando la pipeline AI
    
    Args:
        data: Dati di input con testo da analizzare
        
    Returns:
        Risultati dell'analisi
    """
    try:
        # Usa PipelineManager per inferenza reale
        global _pipeline_manager
        if _pipeline_manager is None:
            _pipeline_manager = PipelineManager(
                model_name="distilbert-base-uncased",
                use_cache=True
            )
        
        result = _pipeline_manager.infer(data.text, postprocess=True)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante analisi: {str(e)}")


@router.get("/status")
def get_ai_status():
    """
    Restituisce lo status corrente dell'AI Core
    
    Returns:
        Status completo del sistema
    """
    status = ai_core.get_status()
    
    # Aggiungi info pipeline se disponibile
    global _pipeline_manager
    if _pipeline_manager:
        status["pipeline"] = _pipeline_manager.get_pipeline_info()
    
    return status

