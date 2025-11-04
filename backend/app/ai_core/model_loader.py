"""
Geko AI Core - Model Loader
Gestisce il caricamento dinamico di modelli AI da varie sorgenti:
- Hugging Face Hub
- Cache locale
- Modelli personalizzati
- Path locali
"""

import os
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime

from .ai_metrics import AIMetrics
from .ai_logger import ai_logger, log_ai_event

try:
    from transformers import AutoModel, AutoTokenizer, AutoConfig
    from transformers.utils import TRANSFORMERS_CACHE
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("[WARN] transformers non installato. Installare con: pip install transformers")

# Configurazione logging
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("geko.ai_core.model_loader")
logger.setLevel(logging.DEBUG)

# Handler per file
file_handler = logging.FileHandler(log_dir / "model_loader.log", encoding='utf-8')
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

# Tipi di modelli supportati
SUPPORTED_MODEL_TYPES = {
    "bert": ["bert-base-uncased", "bert-base-cased", "distilbert-base-uncased"],
    "gpt": ["gpt2", "gpt2-medium"],
    "t5": ["t5-small", "t5-base"],
    "custom": []  # Modelli personalizzati
}

# Cache directory predefinita
DEFAULT_CACHE_DIR = Path.home() / ".geko" / "cache" / "models"


class ModelLoader:
    """
    Classe principale per il caricamento dinamico di modelli AI.
    
    Supporta:
    - Caricamento da Hugging Face Hub
    - Cache locale
    - Modelli personalizzati da path locali
    - Modelli da repository privati
    """
    
    def __init__(
        self,
        model_name: str,
        model_type: Optional[str] = None,
        use_cache: bool = True,
        cache_dir: Optional[Union[str, Path]] = None,
        device: str = "cpu",
        trust_remote_code: bool = False,
        **kwargs
    ):
        """
        Inizializza il ModelLoader.
        
        Args:
            model_name: Nome del modello o path (es. "bert-base-uncased", "./models/my_model")
            model_type: Tipo di modello (es. "bert", "gpt", "custom"). Se None, auto-detect
            use_cache: Se True, usa cache locale se disponibile
            cache_dir: Directory per cache (default: ~/.geko/cache/models)
            device: Device per il modello ("cpu", "cuda", "cuda:0")
            trust_remote_code: Se True, permette esecuzione codice remoto
            **kwargs: Argomenti aggiuntivi per AutoModel.from_pretrained
        """
        self.model_name = model_name
        self.model_type = model_type or self._detect_model_type()
        self.use_cache = use_cache
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.device = device
        self.trust_remote_code = trust_remote_code
        self.kwargs = kwargs
        
        # Crea cache directory se non esiste
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Modello e tokenizer caricati
        self.model = None
        self.tokenizer = None
        self.config = None
        
        self.log_event("info", f"ModelLoader inizializzato per: {model_name}")
    
    def _detect_model_type(self) -> str:
        """Rileva automaticamente il tipo di modello dal nome."""
        model_name_lower = self.model_name.lower()
        
        if "bert" in model_name_lower:
            return "bert"
        elif "gpt" in model_name_lower:
            return "gpt"
        elif "t5" in model_name_lower:
            return "t5"
        elif os.path.isdir(self.model_name) or os.path.isfile(self.model_name):
            return "custom"
        else:
            return "custom"
    
    def log_event(self, level: str, message: str, **kwargs):
        """
        Logga un evento con livello specificato.
        
        Args:
            level: Livello di log ("debug", "info", "warning", "error")
            message: Messaggio da loggare
            **kwargs: Argomenti aggiuntivi
        """
        log_message = message
        if kwargs:
            log_message += f" | {kwargs}"
        
        if level == "debug":
            logger.debug(log_message)
        elif level == "info":
            logger.info(log_message)
        elif level == "warning":
            logger.warning(log_message)
        elif level == "error":
            logger.error(log_message)
        else:
            logger.info(log_message)
    
    def _get_local_model_path(self) -> Optional[Path]:
        """Ottiene il path locale del modello se esiste in cache."""
        if not self.use_cache:
            return None
        
        # Controlla cache directory
        cache_path = self.cache_dir / self.model_name.replace("/", "_")
        if cache_path.exists():
            return cache_path
        
        # Controlla transformers cache
        if TRANSFORMERS_AVAILABLE:
            transformers_cache = Path(TRANSFORMERS_CACHE) if TRANSFORMERS_CACHE else None
            if transformers_cache and transformers_cache.exists():
                # Cerca nella struttura cache di transformers
                for item in transformers_cache.iterdir():
                    if self.model_name.replace("/", "--") in str(item):
                        return item
        
        return None
    
    def _load_from_local_path(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Carica modello da un path locale.
        
        Args:
            path: Path locale al modello
            
        Returns:
            Dict con model, tokenizer, config
        """
        path = Path(path)
        self.log_event("info", f"Caricamento da path locale: {path}")
        
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers non installato")
        
        try:
            config = AutoConfig.from_pretrained(
                str(path),
                trust_remote_code=self.trust_remote_code
            )
            tokenizer = AutoTokenizer.from_pretrained(
                str(path),
                trust_remote_code=self.trust_remote_code
            )
            model = AutoModel.from_pretrained(
                str(path),
                trust_remote_code=self.trust_remote_code,
                **self.kwargs
            )
            
            self.log_event("info", f"Modello caricato con successo da: {path}")
            return {
                "model": model,
                "tokenizer": tokenizer,
                "config": config,
                "source": "local_path"
            }
        except Exception as e:
            self.log_event("error", f"Errore caricamento da path locale: {e}")
            raise
    
    def _load_from_huggingface_hub(self) -> Dict[str, Any]:
        """
        Carica modello da Hugging Face Hub.
        
        Returns:
            Dict con model, tokenizer, config
        """
        self.log_event("info", f"Caricamento da Hugging Face Hub: {self.model_name}")
        
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers non installato")
        
        start_time = time.time()
        
        try:
            # Carica config
            config = AutoConfig.from_pretrained(
                self.model_name,
                cache_dir=str(self.cache_dir),
                trust_remote_code=self.trust_remote_code
            )
            self.log_event("debug", "Config caricato")
            
            # Carica tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=str(self.cache_dir),
                trust_remote_code=self.trust_remote_code
            )
            self.log_event("debug", "Tokenizer caricato")
            
            # Carica modello
            model = AutoModel.from_pretrained(
                self.model_name,
                cache_dir=str(self.cache_dir),
                trust_remote_code=self.trust_remote_code,
                **self.kwargs
            )
            
            load_time = time.time() - start_time
            self.log_event("info", f"Modello caricato da Hugging Face Hub in {load_time:.2f}s")
            
            # Log metriche caricamento
            load_time_ms = load_time * 1000
            log_entry = AIMetrics.log_model_loading(
                model_name=self.model_name,
                load_time_ms=load_time_ms,
                success=True,
                source="huggingface_hub"
            )
            log_ai_event(ai_logger, "model_loading", log_entry, "info")
            
            return {
                "model": model,
                "tokenizer": tokenizer,
                "config": config,
                "source": "huggingface_hub",
                "load_time": load_time
            }
        except Exception as e:
            self.log_event("error", f"Errore caricamento da Hugging Face Hub: {e}")
            raise
    
    def _load_from_remote_url(self) -> Dict[str, Any]:
        """
        Carica modello da URL remoto (es. repository privato).
        
        Returns:
            Dict con model, tokenizer, config
        """
        self.log_event("info", f"Caricamento da URL remoto: {self.model_name}")
        
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers non installato")
        
        try:
            config = AutoConfig.from_pretrained(
                self.model_name,
                cache_dir=str(self.cache_dir),
                trust_remote_code=True
            )
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=str(self.cache_dir),
                trust_remote_code=True
            )
            model = AutoModel.from_pretrained(
                self.model_name,
                cache_dir=str(self.cache_dir),
                trust_remote_code=True,
                **self.kwargs
            )
            
            self.log_event("info", f"Modello caricato da URL remoto")
            return {
                "model": model,
                "tokenizer": tokenizer,
                "config": config,
                "source": "remote_url"
            }
        except Exception as e:
            self.log_event("error", f"Errore caricamento da URL remoto: {e}")
            raise
    
    def load_model(self) -> Dict[str, Any]:
        """
        Carica il modello richiesto, gestendo fallback e cache.
        
        Returns:
            Dict con model, tokenizer, config e metadati
            
        Raises:
            ImportError: Se transformers non è installato
            Exception: Se il caricamento fallisce
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformers non installato. Installare con: pip install transformers"
            )
        
        start_time = time.time()
        
        try:
            # 1. Verifica se è un path locale
            if os.path.isdir(self.model_name) or os.path.isfile(self.model_name):
                result = self._load_from_local_path(self.model_name)
                result["model_type"] = self.model_type
                result["model_name"] = self.model_name
                self.model = result["model"]
                self.tokenizer = result["tokenizer"]
                self.config = result["config"]
                return result
            
            # 2. Verifica se è un URL remoto
            if "https://" in self.model_name or "http://" in self.model_name:
                result = self._load_from_remote_url()
                result["model_type"] = self.model_type
                result["model_name"] = self.model_name
                self.model = result["model"]
                self.tokenizer = result["tokenizer"]
                self.config = result["config"]
                return result
            
            # 3. Controlla cache locale
            if self.use_cache:
                local_path = self._get_local_model_path()
                if local_path:
                    self.log_event("info", f"Trovato modello in cache: {local_path}")
                    try:
                        result = self._load_from_local_path(local_path)
                        result["model_type"] = self.model_type
                        result["model_name"] = self.model_name
                        result["source"] = "cache"
                        self.model = result["model"]
                        self.tokenizer = result["tokenizer"]
                        self.config = result["config"]
                        return result
                    except Exception as e:
                        self.log_event("warning", f"Errore caricamento da cache, fallback a Hub: {e}")
            
            # 4. Fallback a Hugging Face Hub
            self.log_event("info", "Caricamento da Hugging Face Hub (fallback)")
            result = self._load_from_huggingface_hub()
            result["model_type"] = self.model_type
            result["model_name"] = self.model_name
            
            # 5. Salva in cache se richiesto
            if self.use_cache and result["source"] == "huggingface_hub":
                self.log_event("debug", "Modello salvato automaticamente in cache da transformers")
            
            self.model = result["model"]
            self.tokenizer = result["tokenizer"]
            self.config = result["config"]
            
            total_time = time.time() - start_time
            result["total_load_time"] = total_time
            
            self.log_event("info", f"Modello caricato con successo in {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.log_event("error", f"Errore durante caricamento modello: {e}")
            raise
    
    def unload_model(self):
        """Scarica il modello dalla memoria."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if self.config is not None:
            del self.config
            self.config = None
        
        self.log_event("info", "Modello scaricato dalla memoria")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Restituisce informazioni sul modello caricato.
        
        Returns:
            Dict con informazioni modello
        """
        if self.model is None:
            return {
                "status": "not_loaded",
                "model_name": self.model_name
            }
        
        info = {
            "status": "loaded",
            "model_name": self.model_name,
            "model_type": self.model_type,
            "device": self.device,
            "has_tokenizer": self.tokenizer is not None,
            "has_config": self.config is not None
        }
        
        if self.config:
            try:
                info["config"] = {
                    "model_type": getattr(self.config, "model_type", "unknown"),
                    "vocab_size": getattr(self.config, "vocab_size", None),
                    "hidden_size": getattr(self.config, "hidden_size", None)
                }
            except:
                pass
        
        return info


# Funzioni di convenienza per compatibilità con codice esistente
def load_model(
    model_name: str = "bert-base-uncased",
    model_type: Optional[str] = None,
    use_cache: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Funzione di convenienza per caricare un modello.
    
    Args:
        model_name: Nome del modello
        model_type: Tipo di modello (opzionale)
        use_cache: Usa cache se disponibile
        **kwargs: Argomenti aggiuntivi per ModelLoader
        
    Returns:
        Dict con model, tokenizer, config
    """
    loader = ModelLoader(
        model_name=model_name,
        model_type=model_type,
        use_cache=use_cache,
        **kwargs
    )
    return loader.load_model()


def unload_model(loader: ModelLoader):
    """
    Funzione di convenienza per scaricare un modello.
    
    Args:
        loader: Istanza ModelLoader
    """
    loader.unload_model()
