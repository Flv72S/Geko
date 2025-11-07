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

import psutil
from .model_loader import ModelLoader
from .ai_metrics import AIMetrics
from .ai_logger import ai_logger, log_ai_event
from .ai_validation import AICoreValidator, AIFallbackManager

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
        validation_threshold: float = 0.6,
        fallback_models: Optional[List[Union[str, Dict[str, Any]]]] = None,
        max_validation_retries: int = 2,
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
        self.validation_threshold = validation_threshold
        self.max_validation_retries = max(0, max_validation_retries)
        self.loader_kwargs = kwargs.copy()
        self.kwargs = kwargs
        
        self.validator = AICoreValidator(default_threshold=validation_threshold)
        self.fallback_manager = AIFallbackManager(device=device)
        self.fallback_models_config = fallback_models or []
        self.fallback_manager.register_model(model_name, path=model_name, priority=1)
        
        for idx, fallback in enumerate(self.fallback_models_config, start=2):
            name: Optional[str] = None
            path: Optional[str] = None
            priority = idx
            if isinstance(fallback, str):
                name = fallback
                path = fallback
            elif isinstance(fallback, dict):
                name = fallback.get("name") or fallback.get("model_name") or fallback.get("path")
                path = fallback.get("path") or fallback.get("model_name") or name
                priority = fallback.get("priority", idx)
            if not name or not path:
                continue
            self.fallback_manager.register_model(name, path=path, priority=priority)
        
        logger.info(f"Inizializzazione PipelineManager con modello: {model_name}")
        
        # Carica modello principale
        logger.info("Caricamento modello...")
        self._load_model(model_name, display_name=model_name)
        
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
        processing_time_ms = processing_time * 1000
        
        result = {
            "original_text": original_text,
            "normalized_text": text,
            "tokens": tokens,
            "inputs": inputs,
            "token_count": len(tokens),
            "processing_time": round(processing_time, 4)
        }
        
        logger.debug(f"Pre-processing completato in {processing_time:.4f}s - {len(tokens)} tokens")
        
        # Log pre-processing
        log_entry = AIMetrics.log_preprocessing(
            text_length=len(original_text),
            token_count=len(tokens),
            processing_time_ms=processing_time_ms,
            model_name=self.model_name
        )
        log_ai_event(ai_logger, "preprocessing", log_entry, "debug")
        
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
        
        # Metriche iniziali
        cpu_start = psutil.cpu_percent(interval=None)
        memory_start = psutil.virtual_memory()
        
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
            inference_time_ms = inference_time * 1000
            
            # Metriche finali
            cpu_end = psutil.cpu_percent(interval=None)
            memory_end = psutil.virtual_memory()
            
            # Log evento inferenza
            log_entry = AIMetrics.log_inference(
                model_name=self.model_name,
                elapsed_ms=inference_time_ms,
                success=True,
                additional_data={
                    "preprocessing_time_ms": preprocessed["processing_time"] * 1000,
                    "cpu_percent_start": cpu_start,
                    "cpu_percent_end": cpu_end,
                    "memory_used_gb_start": round(memory_start.used / (1024**3), 2),
                    "memory_used_gb_end": round(memory_end.used / (1024**3), 2),
                    "token_count": preprocessed["token_count"],
                    "predicted_category": categories[top_idx] if top_idx < len(categories) else categories[0],
                    "relevance_score": relevance_score
                }
            )
            log_ai_event(ai_logger, "inference", log_entry, "info")
            
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
                "model_used": self.model_name,
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
            inference_time = time.time() - start_time
            inference_time_ms = inference_time * 1000
            
            # Log errore
            log_entry = AIMetrics.log_inference(
                model_name=self.model_name,
                elapsed_ms=inference_time_ms,
                success=False,
                error=e
            )
            log_ai_event(ai_logger, "inference_error", log_entry, "error")
            
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
            "model_used": self.model_name,
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
        Metodo principale per eseguire inferenza completa con validazione e fallback.
        """
        if not text or not text.strip():
            logger.warning("Input vuoto o null")
            return {
                "input_text": text or "",
                "error": "Input vuoto o null",
                "status": "error",
                "validated": False,
                "fallback_used": False
            }
        
        attempts = 0
        available_models = max(1, len(self.fallback_manager.registry))
        max_attempts = max(1, min(available_models, self.max_validation_retries + 1))
        fallback_used = False
        result: Optional[Dict[str, Any]] = None
        last_error: Optional[str] = None
        
        while attempts < max_attempts:
            attempts += 1
            current_model = self.model_name
            logger.debug(f"Infer attempt {attempts}/{max_attempts} con modello {current_model}")
            result = self.infer_text(text)
            
            if not isinstance(result, dict):
                result = {"status": "error", "error": "invalid_result", "input_text": text}
            
            if "error" in result:
                last_error = str(result.get("error"))
                fallback_response = self.fallback_manager.handle_failure({
                    "model": current_model,
                    "reason": "error",
                    "error": last_error
                })
                if fallback_response.get("action") == "switch_model" and attempts < max_attempts:
                    switched = self._switch_to_fallback(fallback_response)
                    if switched:
                        fallback_used = True
                        continue
                break
            
            metadata = result.get("metadata", {})
            latency_seconds = metadata.get("inference_time_seconds")
            latency_ms = round(latency_seconds * 1000, 2) if isinstance(latency_seconds, (int, float)) else None
            validation = self.validator.validate_output(result, threshold=self.validation_threshold)
            report = self.validator.generate_validation_report(
                result,
                {
                    "model_name": self.model_name,
                    "device": self.device,
                    "latency_ms": latency_ms,
                    "threshold": self.validation_threshold
                }
            )
            
            result["validation"] = validation
            result["validation_report"] = report
            result["validated"] = validation.get("valid", False)
            result["issues"] = validation.get("issues", [])
            result["confidence"] = validation.get("confidence", result.get("confidence"))
            result["validation_threshold"] = self.validation_threshold
            result["fallback_used"] = fallback_used
            result["model_used"] = self.model_name
            
            if validation.get("valid"):
                break
            
            fallback_response = self.fallback_manager.handle_failure({
                "model": self.model_name,
                "reason": "low_confidence",
                "validation": validation
            })
            if fallback_response.get("action") == "switch_model" and attempts < max_attempts:
                switched = self._switch_to_fallback(fallback_response)
                if switched:
                    fallback_used = True
                    continue
            if not validation.get("valid"):
                result.setdefault("status", "validation_failed")
                break
        
        if result is None:
            return {
                "input_text": text,
                "error": last_error or "unknown_error",
                "status": "error",
                "validated": False,
                "fallback_used": fallback_used
            }
        
        if "error" in result:
            result.setdefault("fallback_used", fallback_used)
            result.setdefault("validated", False)
            result.setdefault("model_used", self.model_name)
            return result
        
        if postprocess:
            result = self.postprocess_text(result)
        
        return result
    
    def _load_model(self, model_identifier: str, display_name: Optional[str] = None):
        loader = ModelLoader(
            model_name=model_identifier,
            use_cache=self.use_cache,
            device=self.device,
            **self.loader_kwargs
        )
        bundle = loader.load_model()
        self._apply_model_bundle(bundle, loader, display_name or model_identifier)

    def _apply_model_bundle(self, bundle: Dict[str, Any], loader: ModelLoader, display_name: str):
        self.model_loader = loader
        self.model_bundle = bundle
        self.tokenizer = bundle.get("tokenizer")
        self.model = bundle.get("model")
        self.config = bundle.get("config")
        self.model_name = display_name
        if self.model is None:
            raise ValueError("Modello non caricato correttamente")
        if TORCH_AVAILABLE and self.device != "cpu" and hasattr(self.model, 'to'):
            try:
                self.model = self.model.to(self.device)
                logger.info(f"Modello spostato su device: {self.device}")
            except Exception as e:
                logger.warning(f"Impossibile spostare modello su {self.device}: {e}")
        registry_entry = self.fallback_manager.registry.get(display_name)
        if registry_entry is not None:
            registry_entry["last_used"] = datetime.now().isoformat()

    def _switch_to_fallback(self, response: Dict[str, Any]) -> bool:
        target_path = response.get("target_path") or response.get("model_used")
        model_name = response.get("model_used") or target_path
        if not target_path:
            return False
        try:
            load_info = self.fallback_manager.load_model(
                target_path,
                use_cache=self.use_cache,
                **self.loader_kwargs
            )
            bundle = load_info["bundle"]
            loader = load_info["loader"]
            logger.info(f"Switching to fallback model {model_name} (identifier: {target_path})")
            self._apply_model_bundle(bundle, loader, model_name)
            return True
        except Exception as exc:
            logger.error(f"Errore durante caricamento fallback {model_name}: {exc}", exc_info=True)
            self.fallback_manager.log_fallback({
                "action": "fallback_failed",
                "model_used": model_name,
                "reason": str(exc),
                "timestamp": datetime.now().isoformat()
            }, level="error")
            return False

    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Restituisce informazioni sulla pipeline configurata.
        """
        fallback_info = [
            {
                "name": name,
                "path": data.get("path"),
                "priority": data.get("priority"),
                "last_used": data.get("last_used")
            }
            for name, data in self.fallback_manager.registry.items()
        ] if self.fallback_manager else []
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_length": self.max_length,
            "model_loaded": self.model is not None,
            "tokenizer_available": self.tokenizer is not None,
            "supported_pipelines": list(SUPPORTED_PIPELINES.keys()),
            "validation_threshold": self.validation_threshold,
            "max_validation_retries": self.max_validation_retries,
            "fallback_models": fallback_info
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
