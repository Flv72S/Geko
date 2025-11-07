"""Test per AICoreValidator"""

import sys
from pathlib import Path
from datetime import datetime

backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

import pytest
from app.ai_core.ai_validation.validator import AICoreValidator


def _build_sample_output(confidence: float) -> dict:
    return {
        "input_text": "sample",
        "normalized_text": "sample",
        "tokens": ["sample"],
        "token_count": 1,
        "relevance_score": confidence,
        "raw_scores": [confidence, max(0.0, 1 - confidence)],
        "metadata": {
            "timestamp": datetime.now().isoformat()
        }
    }


def test_validate_output_valid():
    validator = AICoreValidator(default_threshold=0.5)
    output = _build_sample_output(0.8)
    result = validator.validate_output(output)
    assert result["valid"] is True
    assert result["confidence"] >= 0.5
    assert result["issues"] == []


def test_validate_output_low_confidence():
    validator = AICoreValidator(default_threshold=0.7)
    output = _build_sample_output(0.4)
    result = validator.validate_output(output)
    assert result["valid"] is False
    assert "threshold" in result
    assert result["confidence"] == pytest.approx(0.6, rel=1e-3)


def test_detect_anomalies():
    validator = AICoreValidator()
    output = {
        "normalized_text": " ",
        "tokens": [],
        "relevance_score": -0.1,
        "raw_scores": [0.2, -0.3]
    }
    issues = validator.detect_anomalies(output)
    assert "empty_normalized_text" in issues
    assert "zero_tokens" in issues
    assert "negative_relevance_score" in issues
    assert "negative_raw_score" in issues


def test_generate_validation_report():
    validator = AICoreValidator(default_threshold=0.6)
    output = _build_sample_output(0.9)
    metadata = {"model_name": "bert-base-uncased", "device": "cpu", "latency_ms": 120}
    report = validator.generate_validation_report(output, metadata)
    assert report["model"] == "bert-base-uncased"
    assert report["device"] == "cpu"
    assert report["valid"] is True
    assert report["status"] == "validated"
