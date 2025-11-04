"""
Geko AI Core - API Routes
Endpoint FastAPI per l'AI Core
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from .pipeline_manager import run_pipeline
from .core_ai import GekoAICore

router = APIRouter(prefix="/ai", tags=["AI Core"])

# Istanza globale AI Core
ai_core = GekoAICore()


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
    result = run_pipeline(data.text)
    return {
        "success": True,
        "result": result
    }


@router.get("/status")
def get_ai_status():
    """
    Restituisce lo status corrente dell'AI Core
    
    Returns:
        Status completo del sistema
    """
    return ai_core.get_status()

