"""
Geko AI Core - Model Loader
Gestisce il caricamento e la gestione dei modelli AI
"""


def load_model(model_name: str = "mock-model"):
    """
    Carica un modello AI
    
    Args:
        model_name: Nome del modello da caricare
        
    Returns:
        Dict con informazioni sul modello caricato
    """
    print(f"[AI Core] Loading model: {model_name}")
    return {
        "model": model_name,
        "status": "loaded",
        "message": f"Model {model_name} loaded successfully"
    }


def unload_model(model_name: str):
    """
    Scarica un modello dalla memoria
    
    Args:
        model_name: Nome del modello da scaricare
    """
    print(f"[AI Core] Unloading model: {model_name}")
    return {
        "model": model_name,
        "status": "unloaded"
    }

