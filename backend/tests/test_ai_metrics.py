"""
Test unitari per AIMetrics
"""

import sys
from pathlib import Path

# Aggiungi backend al path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

import pytest
from app.ai_core.ai_metrics import AIMetrics, format_log_entry


class TestAIMetrics:
    """Test suite per AIMetrics"""
    
    def test_metrics_structure(self):
        """Test struttura metriche"""
        m = AIMetrics.collect_metrics()
        
        assert "cpu_percent" in m
        assert "ram_usage_gb" in m or "ram_used_gb" in m
        assert isinstance(m.get("gpu_available"), bool)
        assert "timestamp" in m
        assert "cpu_count" in m
    
    def test_log_inference_entry(self):
        """Test log entry inferenza"""
        log = AIMetrics.log_inference("bert-base-uncased", 123.45)
        
        assert log["elapsed_ms"] == 123.45
        assert log["model"] == "bert-base-uncased"
        assert log["event"] == "inference"
        assert log["success"] is True
        assert "cpu_percent" in log
        assert "timestamp" in log
    
    def test_log_inference_with_error(self):
        """Test log entry inferenza con errore"""
        error = Exception("Test error")
        log = AIMetrics.log_inference("bert-base-uncased", 50.0, success=False, error=error)
        
        assert log["success"] is False
        assert log["error"] == "Test error"
        assert log["elapsed_ms"] == 50.0
    
    def test_log_preprocessing(self):
        """Test log entry pre-processing"""
        log = AIMetrics.log_preprocessing(
            text_length=100,
            token_count=25,
            processing_time_ms=12.5,
            model_name="bert-base-uncased"
        )
        
        assert log["event"] == "preprocessing"
        assert log["text_length"] == 100
        assert log["token_count"] == 25
        assert log["processing_time_ms"] == 12.5
        assert log["model"] == "bert-base-uncased"
        assert "cpu_percent" in log
    
    def test_log_model_loading(self):
        """Test log entry caricamento modello"""
        log = AIMetrics.log_model_loading(
            model_name="distilbert-base-uncased",
            load_time_ms=500.0,
            success=True,
            source="cache"
        )
        
        assert log["event"] == "model_loading"
        assert log["model"] == "distilbert-base-uncased"
        assert log["load_time_ms"] == 500.0
        assert log["success"] is True
        assert log["source"] == "cache"
    
    def test_get_system_health(self):
        """Test system health status"""
        health = AIMetrics.get_system_health()
        
        assert "status" in health
        assert "warnings" in health
        assert "metrics" in health
        assert "timestamp" in health
        assert health["status"] in ["healthy", "warning", "error"]
        assert isinstance(health["warnings"], list)
    
    def test_format_log_entry(self):
        """Test formattazione log entry"""
        log_entry = {
            "event": "test",
            "message": "Test message",
            "timestamp": "2025-11-04T00:00:00"
        }
        
        formatted = format_log_entry(log_entry)
        
        assert isinstance(formatted, str)
        # Verifica che sia JSON valido
        import json
        parsed = json.loads(formatted)
        assert parsed["event"] == "test"


def test_metrics_collection():
    """Test raccolta metriche base"""
    metrics = AIMetrics.collect_metrics()
    
    assert isinstance(metrics, dict)
    assert "timestamp" in metrics
    assert "cpu_percent" in metrics
    assert metrics["cpu_percent"] >= 0
    assert metrics["cpu_percent"] <= 100


if __name__ == "__main__":
    # Esegui test base senza pytest
    print("=" * 60)
    print("[*] Test AIMetrics - Esecuzione base")
    print("=" * 60)
    
    # Test 1: Raccolta metriche
    print("\n[1] Test raccolta metriche...")
    try:
        metrics = AIMetrics.collect_metrics()
        print(f"    [OK] Metriche raccolte")
        print(f"    CPU: {metrics.get('cpu_percent')}%")
        print(f"    RAM: {metrics.get('ram_used_gb')} GB / {metrics.get('ram_total_gb')} GB")
        print(f"    GPU: {metrics.get('gpu_available')}")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 2: Log inferenza
    print("\n[2] Test log inferenza...")
    try:
        log = AIMetrics.log_inference("bert-base-uncased", 123.45)
        print(f"    [OK] Log entry creato")
        print(f"    Event: {log['event']}")
        print(f"    Model: {log['model']}")
        print(f"    Elapsed: {log['elapsed_ms']}ms")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 3: System health
    print("\n[3] Test system health...")
    try:
        health = AIMetrics.get_system_health()
        print(f"    [OK] Health status: {health['status']}")
        if health['warnings']:
            print(f"    Warnings: {health['warnings']}")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 4: Formattazione
    print("\n[4] Test formattazione log...")
    try:
        log_entry = {"event": "test", "message": "Test"}
        formatted = format_log_entry(log_entry)
        print(f"    [OK] Log formattato come JSON")
        print(f"    Length: {len(formatted)} chars")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    print("\n" + "=" * 60)
    print("[*] Test completati")
    print("=" * 60)

