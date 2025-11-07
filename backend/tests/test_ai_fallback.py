"""Test per AIFallbackManager"""

import sys
from pathlib import Path

backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

import pytest
from app.ai_core.ai_validation.fallback_manager import AIFallbackManager


def test_register_and_list_models():
    fallback = AIFallbackManager()
    fallback.register_model("primary", priority=1)
    fallback.register_model("backup", priority=2)
    models = fallback.list_models()
    assert models[0]["name"] == "primary"
    assert models[1]["name"] == "backup"


def test_handle_failure_switch():
    fallback = AIFallbackManager()
    fallback.register_model("primary", priority=1)
    fallback.register_model("backup", priority=2)
    response = fallback.handle_failure({"model": "primary", "reason": "low_confidence"})
    assert response["action"] == "switch_model"
    assert response["model_used"] == "backup"


def test_handle_failure_no_fallback():
    fallback = AIFallbackManager()
    fallback.register_model("only", priority=1)
    response = fallback.handle_failure({"model": "only", "reason": "error"})
    assert response["action"] == "no_fallback_available"


def test_handle_failure_on_unknown_model():
    fallback = AIFallbackManager()
    fallback.register_model("primary", priority=1)
    response = fallback.handle_failure({"model": "unknown", "reason": "error"})
    assert response["action"] == "switch_model"
    assert response["model_used"] == "primary"
