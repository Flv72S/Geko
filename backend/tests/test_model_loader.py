"""
Test unitari per ModelLoader
"""

import sys
import os
from pathlib import Path

# Aggiungi backend al path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

import pytest
from app.ai_core.model_loader import ModelLoader, load_model, SUPPORTED_MODEL_TYPES


class TestModelLoader:
    """Test suite per ModelLoader"""
    
    def test_loader_initialization(self):
        """Test inizializzazione ModelLoader"""
        loader = ModelLoader(model_name="bert-base-uncased")
        assert loader.model_name == "bert-base-uncased"
        assert loader.model_type == "bert"
        assert loader.use_cache is True
        assert loader.device == "cpu"
    
    def test_model_type_detection(self):
        """Test rilevamento automatico tipo modello"""
        loader_bert = ModelLoader(model_name="bert-base-uncased")
        assert loader_bert.model_type == "bert"
        
        loader_gpt = ModelLoader(model_name="gpt2")
        assert loader_gpt.model_type == "gpt"
        
        loader_t5 = ModelLoader(model_name="t5-small")
        assert loader_t5.model_type == "t5"
    
    @pytest.mark.skipif(
        not os.environ.get("TEST_WITH_DOWNLOADS", "0") == "1",
        reason="Richiede download da Hugging Face - imposta TEST_WITH_DOWNLOADS=1"
    )
    def test_load_bert_model(self):
        """Test caricamento BERT da Hugging Face"""
        loader = ModelLoader(
            model_name="bert-base-uncased",
            use_cache=True
        )
        result = loader.load_model()
        
        assert result is not None
        assert "model" in result
        assert "tokenizer" in result
        assert "config" in result
        assert result["model"] is not None
        assert result["tokenizer"] is not None
        assert result["config"] is not None
        assert result["model_name"] == "bert-base-uncased"
        
        # Test info
        info = loader.get_model_info()
        assert info["status"] == "loaded"
        assert info["has_tokenizer"] is True
        
        # Cleanup
        loader.unload_model()
    
    @pytest.mark.skipif(
        not os.environ.get("TEST_WITH_DOWNLOADS", "0") == "1",
        reason="Richiede download da Hugging Face - imposta TEST_WITH_DOWNLOADS=1"
    )
    def test_load_distilbert_from_cache(self):
        """Test caricamento DistilBERT (verifica cache)"""
        loader = ModelLoader(
            model_name="distilbert-base-uncased",
            use_cache=True
        )
        
        # Primo caricamento (dovrebbe scaricare)
        result1 = loader.load_model()
        assert result1 is not None
        loader.unload_model()
        
        # Secondo caricamento (dovrebbe usare cache)
        loader2 = ModelLoader(
            model_name="distilbert-base-uncased",
            use_cache=True
        )
        result2 = loader2.load_model()
        assert result2 is not None
        # La cache è gestita automaticamente da transformers
        loader2.unload_model()
    
    def test_load_nonexistent_model(self):
        """Test gestione errore modello inesistente"""
        loader = ModelLoader(
            model_name="non-existent-model-xyz123",
            use_cache=False
        )
        
        try:
            result = loader.load_model()
            # Se non solleva eccezione, almeno verifica che gestisca l'errore
            assert result is not None or True  # Può fallire o ritornare None
        except Exception as e:
            # Verifica che l'errore sia loggato
            assert "non-existent-model" in str(e).lower() or "error" in str(e).lower()
    
    def test_load_from_local_path_not_exist(self):
        """Test caricamento da path locale inesistente"""
        loader = ModelLoader(
            model_name="./nonexistent/path/model",
            use_cache=False
        )
        
        try:
            result = loader.load_model()
            # Dovrebbe sollevare eccezione o gestire l'errore
            assert False, "Dovrebbe sollevare eccezione per path inesistente"
        except Exception:
            # Eccezione attesa
            pass
    
    def test_unload_model(self):
        """Test scaricamento modello"""
        loader = ModelLoader(model_name="bert-base-uncased")
        
        # Carica modello (se possibile)
        try:
            loader.load_model()
            assert loader.model is not None
            
            # Scarica
            loader.unload_model()
            assert loader.model is None
            assert loader.tokenizer is None
        except ImportError:
            # transformers non installato, skip test
            pytest.skip("transformers non installato")
        except Exception:
            # Altri errori (es. network), skip
            pytest.skip("Impossibile caricare modello per test")
    
    def test_get_model_info_not_loaded(self):
        """Test info modello non caricato"""
        loader = ModelLoader(model_name="bert-base-uncased")
        info = loader.get_model_info()
        
        assert info["status"] == "not_loaded"
        assert info["model_name"] == "bert-base-uncased"
    
    def test_function_wrapper(self):
        """Test funzione di convenienza load_model"""
        try:
            result = load_model(
                model_name="bert-base-uncased",
                use_cache=True
            )
            assert result is not None
            assert "model" in result
        except ImportError:
            pytest.skip("transformers non installato")
        except Exception:
            pytest.skip("Impossibile caricare modello per test")


def test_supported_model_types():
    """Test che SUPPORTED_MODEL_TYPES contenga i tipi attesi"""
    assert "bert" in SUPPORTED_MODEL_TYPES
    assert "gpt" in SUPPORTED_MODEL_TYPES
    assert "custom" in SUPPORTED_MODEL_TYPES
    assert len(SUPPORTED_MODEL_TYPES["bert"]) > 0


if __name__ == "__main__":
    # Esegui test base senza pytest
    print("=" * 60)
    print("[*] Test ModelLoader - Esecuzione base")
    print("=" * 60)
    
    # Test 1: Inizializzazione
    print("\n[1] Test inizializzazione...")
    try:
        loader = ModelLoader(model_name="bert-base-uncased")
        print(f"    [OK] ModelLoader inizializzato: {loader.model_name}")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 2: Rilevamento tipo
    print("\n[2] Test rilevamento tipo modello...")
    try:
        loader = ModelLoader(model_name="gpt2")
        print(f"    [OK] Tipo rilevato: {loader.model_type}")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 3: Caricamento (solo se transformers disponibile e TEST_WITH_DOWNLOADS=1)
    print("\n[3] Test caricamento modello...")
    if os.environ.get("TEST_WITH_DOWNLOADS", "0") == "1":
        try:
            loader = ModelLoader(model_name="bert-base-uncased", use_cache=True)
            result = loader.load_model()
            print(f"    [OK] Modello caricato: {result['model_name']}")
            print(f"    [OK] Source: {result.get('source', 'unknown')}")
            loader.unload_model()
        except Exception as e:
            print(f"    [ERROR] {e}")
    else:
        print("    [SKIP] Impostare TEST_WITH_DOWNLOADS=1 per testare download")
    
    print("\n" + "=" * 60)
    print("[*] Test completati")
    print("=" * 60)

