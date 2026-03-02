from typing import Dict, Tuple

from api.models.response import LayerResult

BASE_SCORE = 50

USE_CASE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "banking": {
        "identity": 1.5,
        "integrity": 2.0,
        "context": 1.0,
        "quality": 0.5,
        "ai": 1.5,
    },
    "enterprise": {
        "identity": 1.0,
        "integrity": 1.5,
        "context": 1.5,
        "quality": 1.0,
        "ai": 1.0,
    },
    "emergency": {
        "identity": 0.5,
        "integrity": 0.5,
        "context": 2.0,
        "quality": 2.0,
        "ai": 0.5,
    },
    "generic": {
        "identity": 1.0,
        "integrity": 1.0,
        "context": 1.0,
        "quality": 1.0,
        "ai": 1.0,
    },
}


def _clamp_score(score: int) -> int:
    return max(0, min(100, score))


def badge_for_score(score: int) -> str:
    if score >= 70:
        return "TRUSTED"
    if score >= 40:
        return "CAUTION"
    return "UNTRUSTED"


def ttl_for_use_case(use_case: str) -> int:
    use_case_key = use_case.lower()
    if use_case_key == "banking":
        return 120
    if use_case_key == "enterprise":
        return 600
    if use_case_key == "emergency":
        return 0
    return 300


def confidence_from_layers(layer_results: Dict[str, LayerResult]) -> float:
    layer_count = max(1, len(layer_results))
    healthy_layers = sum(1 for layer in layer_results.values() if layer.error is None)
    confidence = healthy_layers / layer_count
    return max(0.0, min(1.0, round(confidence, 3)))


def compute_score(layer_results: Dict[str, LayerResult], use_case: str) -> Tuple[int, Dict[str, int]]:
    weights = USE_CASE_WEIGHTS.get(use_case.lower(), USE_CASE_WEIGHTS["generic"])
    weighted_deltas: Dict[str, int] = {}

    score = BASE_SCORE
    for layer_name, layer_result in layer_results.items():
        weight = weights.get(layer_name, 1.0)
        weighted_delta = int(round(layer_result.score_delta * weight))
        weighted_deltas[layer_name] = weighted_delta
        score += weighted_delta

    return _clamp_score(score), weighted_deltas
