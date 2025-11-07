"""
Validator per Geko AI Core
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
from logging.handlers import RotatingFileHandler


def _setup_validator_logger() -> logging.Logger:
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "ai_validation.log"
    logger = logging.getLogger("geko.ai_core.validation")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


validator_logger = _setup_validator_logger()


class AICoreValidator:
    """Valida output pipeline AI e genera report diagnostico."""

    def __init__(self, default_threshold: float = 0.6):
        self.default_threshold = default_threshold

    def validate_output(self, output: Dict[str, Any], threshold: Optional[float] = None) -> Dict[str, Any]:
        threshold = threshold or self.default_threshold
        scores = self._extract_scores(output)
        confidence = self.compute_confidence(scores)
        issues = self.detect_anomalies(output)
        valid = confidence >= threshold and not issues
        result = {
            "valid": valid,
            "confidence": round(confidence, 4),
            "threshold": threshold,
            "issues": issues,
            "timestamp": datetime.now().isoformat(),
        }
        validator_logger.info(json.dumps({"event": "validation", **result}))
        return result

    def compute_confidence(self, scores: Optional[List[float]]) -> float:
        if not scores:
            return 0.0
        safe_scores = [max(0.0, min(1.0, float(s))) for s in scores if not math.isnan(s)]
        if not safe_scores:
            return 0.0
        return float(max(safe_scores))

    def detect_anomalies(self, output: Dict[str, Any]) -> List[str]:
        issues: List[str] = []
        if not output:
            issues.append("output_empty")
            return issues
        relevance = output.get("relevance_score")
        if relevance is None or not isinstance(relevance, (int, float)):
            issues.append("missing_relevance_score")
        elif relevance < 0:
            issues.append("negative_relevance_score")
        tokens = output.get("tokens")
        if isinstance(tokens, list) and len(tokens) == 0:
            issues.append("zero_tokens")
        normalized_text = output.get("normalized_text")
        if isinstance(normalized_text, str) and not normalized_text.strip():
            issues.append("empty_normalized_text")
        raw_scores = output.get("raw_scores")
        if isinstance(raw_scores, list):
            if any((not isinstance(s, (int, float))) for s in raw_scores):
                issues.append("invalid_raw_scores")
            if any(s < 0 for s in raw_scores if isinstance(s, (int, float))):
                issues.append("negative_raw_score")
        return issues

    def generate_validation_report(self, output: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        metadata = metadata or {}
        validation = self.validate_output(output, threshold=metadata.get("threshold"))
        report = {
            "model": metadata.get("model_name"),
            "status": "validated" if validation["valid"] else "rejected",
            "confidence": validation["confidence"],
            "latency_ms": metadata.get("latency_ms"),
            "device": metadata.get("device"),
            "valid": validation["valid"],
            "issues": validation["issues"],
            "timestamp": validation["timestamp"],
        }
        validator_logger.info(json.dumps({"event": "validation_report", **report}))
        return report

    def _extract_scores(self, output: Dict[str, Any]) -> Optional[List[float]]:
        raw_scores = output.get("raw_scores")
        if isinstance(raw_scores, list) and raw_scores:
            return [float(s) for s in raw_scores if isinstance(s, (int, float))]
        confidence = output.get("confidence")
        if isinstance(confidence, (int, float)):
            return [float(confidence)]
        return None
