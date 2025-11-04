"""
Geko AI Core - Pipeline Manager
Gestisce il flusso di elaborazione dati attraverso la pipeline AI
"""

from .model_loader import ModelLoader, load_model


def preprocess(input_text: str):
    """
    Pre-processing dei dati di input
    
    Args:
        input_text: Testo grezzo da processare
        
    Returns:
        Dati processati
    """
    # Normalizzazione base
    processed = input_text.strip()
    return {
        "original": input_text,
        "processed": processed,
        "length": len(processed)
    }


def inference(model_data, processed_data):
    """
    Esegue inferenza usando il modello
    
    Args:
        model_data: Dict con model, tokenizer, config (da ModelLoader)
        processed_data: Dati processati
        
    Returns:
        Risultati inferenza
    """
    model = model_data.get("model")
    tokenizer = model_data.get("tokenizer")
    model_name = model_data.get("model_name", "unknown")
    
    # Mock inference (da implementare con logica reale)
    return {
        "model": model_name,
        "result": "inference_ok",
        "confidence": 0.95,
        "note": "Mock inference - implementare logica reale"
    }


def postprocess(inference_result):
    """
    Post-processing dei risultati
    
    Args:
        inference_result: Risultati dell'inferenza
        
    Returns:
        Risultati formattati
    """
    return {
        **inference_result,
        "formatted": True,
        "timestamp": None
    }


def run_pipeline(input_text: str):
    """
    Esegue l'intera pipeline: pre-processing -> inference -> post-processing
    
    Args:
        input_text: Testo di input
        
    Returns:
        Risultati completi della pipeline
    """
    print("[AI Core] Running pipeline...")
    
    # Step 1: Pre-processing
    processed = preprocess(input_text)
    
    # Step 2: Load model
    model_data = load_model()
    model = model_data.get("model")
    tokenizer = model_data.get("tokenizer")
    
    # Step 3: Inference
    inference_result = inference(model_data, processed)
    
    # Step 4: Post-processing
    final_result = postprocess(inference_result)
    
    return {
        "input": input_text,
        "preprocessed": processed,
        "model": model["model"],
        "inference": inference_result,
        "result": "pipeline_ok",
        "final_output": final_result
    }

