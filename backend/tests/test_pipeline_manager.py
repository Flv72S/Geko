"""
Test unitari per PipelineManager
"""

import sys
import os
from pathlib import Path

# Aggiungi backend al path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

import pytest
from app.ai_core.pipeline_manager import PipelineManager, run_pipeline, SUPPORTED_PIPELINES


class TestPipelineManager:
    """Test suite per PipelineManager"""
    
    @pytest.mark.skipif(
        not os.environ.get("TEST_WITH_DOWNLOADS", "0") == "1",
        reason="Richiede download modello - imposta TEST_WITH_DOWNLOADS=1"
    )
    def test_pipeline_basic_inference(self):
        """Test inferenza base con testo semplice"""
        pm = PipelineManager(model_name="distilbert-base-uncased", use_cache=True)
        result = pm.infer("This is a test sentence.")
        
        assert "predicted_category" in result
        assert "relevance_score" in result
        assert isinstance(result.get("raw_scores"), list)
        assert "metadata" in result
        assert "input_text" in result
    
    def test_pipeline_initialization(self):
        """Test inizializzazione PipelineManager"""
        try:
            pm = PipelineManager(model_name="bert-base-uncased", use_cache=False)
            assert pm.model_name == "bert-base-uncased"
            assert pm.device == "cpu"
            assert pm.max_length == 128
        except Exception as e:
            # Se transformers non installato, skip
            if "transformers" in str(e).lower() or "import" in str(e).lower():
                pytest.skip("transformers non installato")
            raise
    
    def test_preprocess_text(self):
        """Test tokenizzazione corretta"""
        try:
            pm = PipelineManager(model_name="bert-base-uncased", use_cache=False)
            
            text = "This is a test sentence with special characters !@#$%"
            result = pm.preprocess_text(text)
            
            assert "original_text" in result
            assert "normalized_text" in result
            assert "tokens" in result
            assert isinstance(result["tokens"], list)
            assert result["token_count"] > 0
            assert "processing_time" in result
        except Exception as e:
            if "transformers" in str(e).lower() or "import" in str(e).lower():
                pytest.skip("transformers non installato")
            raise
    
    def test_infer_empty_input(self):
        """Test gestione input vuoti o nulli"""
        try:
            pm = PipelineManager(model_name="bert-base-uncased", use_cache=False)
            
            # Test input vuoto
            result_empty = pm.infer("")
            assert "error" in result_empty or "status" in result_empty
            
            # Test input None (simulato)
            result_none = pm.infer("   ")
            assert "error" in result_none or "status" in result_none
        except Exception as e:
            if "transformers" in str(e).lower() or "import" in str(e).lower():
                pytest.skip("transformers non installato")
            raise
    
    def test_postprocess_text(self):
        """Test post-processing risultati"""
        try:
            pm = PipelineManager(model_name="bert-base-uncased", use_cache=False)
            
            mock_result = {
                "input_text": "test",
                "predicted_category": "general",
                "relevance_score": 0.95
            }
            
            result = pm.postprocess_text(mock_result)
            
            assert result["formatted"] is True
            assert "formatted_at" in result
            assert "confidence_level" in result
            assert result["confidence_level"] == "high"  # 0.95 >= 0.8
        except Exception as e:
            if "transformers" in str(e).lower() or "import" in str(e).lower():
                pytest.skip("transformers non installato")
            raise
    
    def test_get_pipeline_info(self):
        """Test informazioni pipeline"""
        try:
            pm = PipelineManager(model_name="bert-base-uncased", use_cache=False)
            info = pm.get_pipeline_info()
            
            assert "model_name" in info
            assert "device" in info
            assert "max_length" in info
            assert "model_loaded" in info
            assert "supported_pipelines" in info
        except Exception as e:
            if "transformers" in str(e).lower() or "import" in str(e).lower():
                pytest.skip("transformers non installato")
            raise
    
    def test_run_pipeline_function(self):
        """Test funzione di convenienza run_pipeline"""
        try:
            result = run_pipeline(
                "This is a test.",
                model_name="bert-base-uncased",
                use_cache=False
            )
            assert "input_text" in result
            assert "predicted_category" in result or "error" in result
        except Exception as e:
            if "transformers" in str(e).lower() or "import" in str(e).lower():
                pytest.skip("transformers non installato")
            raise

    def test_pipeline_infer_with_validation_and_fallback(self, monkeypatch):
        """Simula inferenza con fallback automatico"""

        def fake_load_model(self, model_identifier, display_name=None):
            self.model_loader = None
            self.model_bundle = {"model_type": "mock"}
            self.tokenizer = None
            self.model = object()
            self.config = {}
            self.model_name = display_name or model_identifier
            if self.fallback_manager and self.model_name in self.fallback_manager.registry:
                self.fallback_manager.registry[self.model_name]["last_used"] = "mock"

        def fake_switch_to_fallback(self, response):
            target = response.get("model_used") or "mock-fallback"
            if target not in self.fallback_manager.registry:
                self.fallback_manager.register_model(target, path=target, priority=5)
            self.fallback_manager.registry[target]["last_used"] = "mock"
            self.model_name = target
            return True

        def fake_infer_text(self, text):
            base = {
                "input_text": text,
                "normalized_text": text.lower(),
                "tokens": text.lower().split(),
                "token_count": max(1, len(text.split())),
                "categories": ["general", "technical"],
                "predicted_category": "general",
                "raw_scores": [],
                "relevance_score": 0.0,
                "confidence": 0.0,
                "metadata": {"inference_time_seconds": 0.05},
                "model_used": self.model_name
            }
            if self.model_name == "distilbert-base-uncased":
                base["raw_scores"] = [0.3, 0.2]
                base["relevance_score"] = 0.3
                base["confidence"] = 0.3
            else:
                base["raw_scores"] = [0.9, 0.1]
                base["relevance_score"] = 0.9
                base["confidence"] = 0.9
            return base

        monkeypatch.setattr(PipelineManager, "_load_model", fake_load_model, raising=False)
        monkeypatch.setattr(PipelineManager, "_switch_to_fallback", fake_switch_to_fallback, raising=False)
        monkeypatch.setattr(PipelineManager, "infer_text", fake_infer_text, raising=False)

        pm = PipelineManager(
            model_name="distilbert-base-uncased",
            use_cache=False,
            fallback_models=[{"name": "mock-fallback", "priority": 2}],
            validation_threshold=0.6,
            max_validation_retries=2
        )

        result = pm.infer("Test fallback validation")
        assert result["validated"] is True
        assert result["fallback_used"] is True
        assert result["model_used"] == "mock-fallback"
        assert result["issues"] == []


def test_supported_pipelines():
    """Test che SUPPORTED_PIPELINES contenga i tipi attesi"""
    assert "text" in SUPPORTED_PIPELINES
    assert "image" in SUPPORTED_PIPELINES
    assert "audio" in SUPPORTED_PIPELINES
    assert "preprocess" in SUPPORTED_PIPELINES["text"]
    assert "infer" in SUPPORTED_PIPELINES["text"]


if __name__ == "__main__":
    # Esegui test base senza pytest
    print("=" * 60)
    print("[*] Test PipelineManager - Esecuzione base")
    print("=" * 60)
    
    # Test 1: Inizializzazione
    print("\n[1] Test inizializzazione...")
    try:
        pm = PipelineManager(model_name="bert-base-uncased", use_cache=False)
        print(f"    [OK] PipelineManager inizializzato: {pm.model_name}")
        print(f"    [OK] Device: {pm.device}, Max length: {pm.max_length}")
    except Exception as e:
        print(f"    [ERROR] {e}")
        print(f"    [INFO] transformers potrebbe non essere installato")
    
    # Test 2: Pre-processing
    print("\n[2] Test pre-processing...")
    try:
        pm = PipelineManager(model_name="bert-base-uncased", use_cache=False)
        text = "This is a test sentence with special chars !@#$"
        result = pm.preprocess_text(text)
        print(f"    [OK] Pre-processing completato")
        print(f"    [OK] Tokens: {len(result['tokens'])}")
        print(f"    [OK] Tempo: {result['processing_time']}s")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 3: Inferenza (solo se TEST_WITH_DOWNLOADS=1)
    print("\n[3] Test inferenza...")
    if os.environ.get("TEST_WITH_DOWNLOADS", "0") == "1":
        try:
            pm = PipelineManager(model_name="distilbert-base-uncased", use_cache=True)
            result = pm.infer("This is a test sentence for inference.")
            print(f"    [OK] Inferenza completata")
            print(f"    [OK] Categoria predetta: {result.get('predicted_category')}")
            print(f"    [OK] Relevance score: {result.get('relevance_score')}")
            print(f"    [OK] Confidence: {result.get('confidence_level')}")
        except Exception as e:
            print(f"    [ERROR] {e}")
    else:
        print("    [SKIP] Impostare TEST_WITH_DOWNLOADS=1 per testare inferenza reale")
    
    # Test 4: Gestione input vuoto
    print("\n[4] Test gestione input vuoto...")
    try:
        pm = PipelineManager(model_name="bert-base-uncased", use_cache=False)
        result = pm.infer("")
        if "error" in result:
            print(f"    [OK] Errore gestito correttamente: {result['error']}")
        else:
            print(f"    [OK] Input vuoto gestito")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    print("\n" + "=" * 60)
    print("[*] Test completati")
    print("=" * 60)

