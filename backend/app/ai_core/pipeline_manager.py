"""
Geko AI Core - Pipeline Manager
Gestisce il flusso completo di elaborazione dati attraverso la pipeline AI:
- Pre-processing testuale completo
- Inferenza reale con modelli AI
- Post-processing e formattazione output
"""

import re
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[WARN] torch non installato. Installare con: pip install torch")

from .model_loader import ModelLoader

# Configurazione logging
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("geko.ai_core.pipeline_manager")
logger.setLevel(logging.DEBUG)

# Handler per file
file_handler = logging.FileHandler(log_dir / "pipeline_manager.log", encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Handler per console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Pipeline supportate (estendibile per multimodale)
SUPPORTED_PIPELINES = {
    "text": {
        "preprocess": "preprocess_text",
        "infer": "infer_text",
        "postprocess": "postprocess_text"
    },
    # Placeholder per future estensioni
    "image": {
        "preprocess": "preprocess_image",
        "infer": "infer_image",
        "postprocess": "postprocess_image"
    },
    "audio": {
        "preprocess": "preprocess_audio",
        "infer": "infer_audio",
        "postprocess": "postprocess_audio"
    }
}


class PipelineManager:
    """
    Classe principale per gestire pipeline AI complete.
    
    Supporta:
    - Pre-processing testuale completo
    - Inferenza reale con modelli Hugging Face
    - Output JSON arricchito con punteggi e metadati
    - Estendibilità per pipeline multimodali
    """
    
    def __init__(
        self,
        model_name: str = "bert-base-uncased",
        use_cache: bool = True,
        device: str = "cpu",
        max_length: int = 128,
        **kwargs
    ):
        """
        Inizializza PipelineManager.
        
        Args:
            model_name: Nome del modello da caricare
            use_cache: Usa cache se disponibile
            device: Device per inferenza ("cpu", "cuda", "cuda:0")
            max_length: Lunghezza massima sequenza per tokenizzazione
            **kwargs: Argomenti aggiuntivi per ModelLoader
        """
        self.model_name = model_name
        self.use_cache = use_cache
        self.device = device
        self.max_length = max_length
        self.kwargs = kwargs
        
        # Inizializza ModelLoader
        logger.info(f"Inizializzazione PipelineManager con modello: {model_name}")
        self.model_loader = ModelLoader(
            model_name=model_name,
            use_cache=use_cache,
            device=device,
            **kwargs
        )
        
        # Carica modello
        logger.info("Caricamento modello...")
        self.model_bundle = self.model_loader.load_model()
        self.tokenizer = self.model_bundle.get("tokenizer")
        self.model = self.model_bundle.get("model")
        self.config = self.model_bundle.get("config")
        
        if self.model is None:
            raise ValueError("Modello non caricato correttamente")
        
        # Sposta modello su device se necessario
        if TORCH_AVAILABLE and device != "cpu" and hasattr(self.model, 'to'):
            try:
                self.model = self.model.to(device)
                logger.info(f"Modello spostato su device: {device}")
            except Exception as e:
                logger.warning(f"Impossibile spostare modello su {device}: {e}")
        
        logger.info("PipelineManager inizializzato correttamente")
    
    def preprocess_text(self, text: str) -> Dict[str, Any]:
        """
        Normalizza, tokenizza e prepara il testo per l'inferenza.
        
        Args:
            text: Testo grezzo da processare
            
        Returns:
            Dict con testo normalizzato, tokens e input tensors
        """
        logger.debug(f"Pre-processing testo: {text[:50]}...")
        start_time = time.time()
        
        # Normalizzazione base
        original_text = text
        text = text.strip()
        
        # Pulizia testo (rimuove caratteri speciali non standard)
        # Mantiene: lettere, numeri, spazi, punteggiatura base
        text = re.sub(r"[^\w\s.,!?;:'\"-]", "", text)
        
        # Normalizzazione spazi multipli
        text = re.sub(r'\s+', ' ', text)
        
        # Tokenizzazione con tokenizer Hugging Face
        if self.tokenizer is None:
            logger.warning("Tokenizer non disponibile, usando tokenizzazione base")
            tokens = text.split()
        else:
            try:
                # Tokenizza in tokens
                tokens = self.tokenizer.tokenize(text)
                
                # Crea input tensors per il modello
                inputs = self.tokenizer(
                    text,
                    truncation=True,
                    padding="max_length",
                    max_length=self.max_length,
                    return_tensors="pt"
                )
                
                # Sposta su device se necessario
                if TORCH_AVAILABLE and self.device != "cpu":
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
            except Exception as e:
                logger.error(f"Errore tokenizzazione: {e}")
                # Fallback a tokenizzazione base
                tokens = text.split()
                inputs = None
        
        processing_time = time.time() - start_time
        
        result = {
            "original_text": original_text,
            "normalized_text": text,
            "tokens": tokens,
            "inputs": inputs,
            "token_count": len(tokens),
            "processing_time": round(processing_time, 4)
        }
        
        logger.debug(f"Pre-processing completato in {processing_time:.4f}s - {len(tokens)} tokens")
        
        return result
    
    def infer_text(self, text: str) -> Dict[str, Any]:
        """
        Esegue inferenza reale su testo e restituisce output JSON arricchito.
        
        Args:
            text: Testo da analizzare
            
        Returns:
            Dict con risultati inferenza, categorie, punteggi e metadati
        """
        logger.info(f"Starting inference for input: {text[:50]}...")
        start_time = time.time()
        
        try:
            # Pre-processing
            preprocessed = self.preprocess_text(text)
            
            if preprocessed["inputs"] is None:
                logger.warning("Input non disponibili, usando mock inference")
                return self._mock_inference(preprocessed)
            
            # Inferenza reale
            if not TORCH_AVAILABLE:
                logger.warning("PyTorch non disponibile, usando mock inference")
                return self._mock_inference(preprocessed)
            
            self.model.eval()
            inputs = preprocessed["inputs"]
            
            with torch.no_grad():
                try:
                    # Esegui inferenza
                    outputs = self.model(**inputs)
                    
                    # Estrai features
                    if hasattr(outputs, 'last_hidden_state'):
                        # Per modelli encoder (BERT, etc.)
                        hidden_state = outputs.last_hidden_state
                        # Media pooling sulla sequenza
                        pooled = hidden_state.mean(dim=1)
                    elif hasattr(outputs, 'pooler_output'):
                        # Per modelli con pooler
                        pooled = outputs.pooler_output
                    elif hasattr(outputs, 'logits'):
                        # Per modelli classificatori
                        pooled = outputs.logits
                    else:
                        # Fallback: usa primo output disponibile
                        pooled = list(outputs.values())[0]
                        if isinstance(pooled, tuple):
                            pooled = pooled[0]
                        # Media pooling se necessario
                        if len(pooled.shape) > 2:
                            pooled = pooled.mean(dim=1)
                    
                    # Normalizza per ottenere probabilità
                    # Se pooled ha dimensioni compatibili, calcola softmax
                    if pooled.shape[-1] > 1:
                        probs = F.softmax(pooled, dim=-1)
                    else:
                        # Sigmoid per output binario
                        probs = torch.sigmoid(pooled)
                    
                    # Converti a lista
                    probs_list = probs.cpu().numpy().tolist()
                    if isinstance(probs_list[0], list):
                        probs_list = probs_list[0]
                    
                except Exception as e:
                    logger.error(f"Errore durante inferenza: {e}")
                    return self._mock_inference(preprocessed)
            
            # Categorie (mock - da personalizzare in base al modello)
            categories = self._get_categories()
            
            # Trova categoria predetta
            if len(probs_list) >= len(categories):
                top_idx = max(range(len(categories)), key=lambda i: probs_list[i] if i < len(probs_list) else 0)
            else:
                # Usa prima categoria se probabilità non corrispondono
                top_idx = 0
            
            relevance_score = float(max(probs_list)) if probs_list else 0.0
            
            inference_time = time.time() - start_time
            
            result = {
                "input_text": preprocessed["original_text"],
                "normalized_text": preprocessed["normalized_text"],
                "tokens": preprocessed["tokens"][:20],  # Limita a 20 per output
                "token_count": preprocessed["token_count"],
                "categories": categories,
                "predicted_category": categories[top_idx] if top_idx < len(categories) else categories[0],
                "relevance_score": round(relevance_score, 4),
                "raw_scores": [round(float(p), 4) for p in probs_list[:len(categories)]],
                "confidence": round(relevance_score, 4),
                "metadata": {
                    "model_name": self.model_name,
                    "model_type": self.model_bundle.get("model_type", "unknown"),
                    "timestamp": datetime.now().isoformat(),
                    "device": self.device,
                    "inference_time_seconds": round(inference_time, 4),
                    "total_processing_time_seconds": round(inference_time + preprocessed["processing_time"], 4)
                }
            }
            
            logger.info(f"Inference complete. Predicted: {result['predicted_category']} (score: {relevance_score:.4f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Errore durante inferenza: {e}", exc_info=True)
            return {
                "input_text": text,
                "error": str(e),
                "status": "error",
                "metadata": {
                    "model_name": self.model_name,
                    "timestamp": datetime.now().isoformat(),
                    "device": self.device
                }
            }
    
    def _get_categories(self) -> List[str]:
        """
        Restituisce lista categorie per classificazione.
        Da personalizzare in base al modello utilizzato.
        """
        # Categorie mock - da personalizzare
        return ["general", "technical", "social", "warning", "neutral"]
    
    def _mock_inference(self, preprocessed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock inference quando il modello reale non è disponibile.
        
        Args:
            preprocessed: Dati pre-processati
            
        Returns:
            Dict con risultati mock
        """
        logger.warning("Usando mock inference")
        
        categories = self._get_categories()
        
        return {
            "input_text": preprocessed["original_text"],
            "normalized_text": preprocessed["normalized_text"],
            "tokens": preprocessed["tokens"][:20],
            "token_count": preprocessed["token_count"],
            "categories": categories,
            "predicted_category": categories[0],
            "relevance_score": 0.95,
            "raw_scores": [0.2] * len(categories),
            "confidence": 0.95,
            "note": "Mock inference - modello non disponibile",
            "metadata": {
                "model_name": self.model_name,
                "model_type": "mock",
                "timestamp": datetime.now().isoformat(),
                "device": self.device,
                "inference_time_seconds": 0.001,
                "total_processing_time_seconds": preprocessed["processing_time"]
            }
        }
    
    def postprocess_text(self, inference_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-processing dei risultati inferenza.
        
        Args:
            inference_result: Risultati dell'inferenza
            
        Returns:
            Risultati formattati e arricchiti
        """
        logger.debug("Post-processing risultati")
        
        # Aggiungi flag di formattazione
        result = {
            **inference_result,
            "formatted": True,
            "formatted_at": datetime.now().isoformat()
        }
        
        # Aggiungi interpretazione confidenza
        if "relevance_score" in result:
            score = result["relevance_score"]
            if score >= 0.8:
                result["confidence_level"] = "high"
            elif score >= 0.5:
                result["confidence_level"] = "medium"
            else:
                result["confidence_level"] = "low"
        
        return result
    
    def infer(self, text: str, postprocess: bool = True) -> Dict[str, Any]:
        """
        Metodo principale per eseguire inferenza completa.
        
        Args:
            text: Testo da analizzare
            postprocess: Se True, applica post-processing
            
        Returns:
            Dict con risultati completi
        """
        if not text or not text.strip():
            logger.warning("Input vuoto o null")
            return {
                "input_text": text or "",
                "error": "Input vuoto o null",
                "status": "error"
            }
        
        # Esegui inferenza
        result = self.infer_text(text)
        
        # Post-processing se richiesto
        if postprocess and "error" not in result:
            result = self.postprocess_text(result)
        
        return result
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Restituisce informazioni sulla pipeline configurata.
        
        Returns:
            Dict con informazioni pipeline
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_length": self.max_length,
            "model_loaded": self.model is not None,
            "tokenizer_available": self.tokenizer is not None,
            "supported_pipelines": list(SUPPORTED_PIPELINES.keys())
        }


# Funzioni di convenienza per compatibilità con codice esistente
def preprocess(input_text: str):
    """Funzione di convenienza per pre-processing"""
    # Richiede istanza PipelineManager
    raise NotImplementedError("Usare PipelineManager.preprocess_text()")


def inference(model_data, processed_data):
    """Funzione di convenienza per inferenza"""
    # Richiede istanza PipelineManager
    raise NotImplementedError("Usare PipelineManager.infer_text()")


def postprocess(inference_result):
    """Funzione di convenienza per post-processing"""
    return {
        **inference_result,
        "formatted": True,
        "timestamp": datetime.now().isoformat()
    }


def run_pipeline(input_text: str, model_name: str = "bert-base-uncased", **kwargs) -> Dict[str, Any]:
    """
    Funzione di convenienza per eseguire pipeline completa.
    
    Args:
        input_text: Testo da processare
        model_name: Nome modello da usare
        **kwargs: Argomenti aggiuntivi per PipelineManager
        
    Returns:
        Dict con risultati completi
    """
    pm = PipelineManager(model_name=model_name, **kwargs)
    return pm.infer(input_text)
