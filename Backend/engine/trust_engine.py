import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import uuid4

from api.models.request import TrustCallRequest
from api.models.response import LayerResult, TrustCallResponse
from engine.layers.ai_layer import AILayer
from engine.layers.context import ContextLayer
from engine.layers.identity import IdentityLayer
from engine.layers.integrity import IntegrityLayer
from engine.layers.quality import QualityLayer
from engine.score import badge_for_score, compute_score, confidence_from_layers, ttl_for_use_case


class TrustCallEngine:
    def __init__(self) -> None:
        self.identity_layer = IdentityLayer()
        self.integrity_layer = IntegrityLayer()
        self.context_layer = ContextLayer()
        self.quality_layer = QualityLayer()
        self.ai_layer = AILayer()

    async def run(self, request: TrustCallRequest, request_id: Optional[str] = None) -> TrustCallResponse:
        request_id_value = request_id or str(uuid4())
        requested = set(request.requested_layers)

        identity_task = self.identity_layer.evaluate(request.phone_number, request.kyc_data)
        integrity_task = self.integrity_layer.evaluate(request.phone_number)
        context_task = self.context_layer.evaluate(request.phone_number, request.claimed_location)
        quality_task = self.quality_layer.evaluate(request.phone_number)

        identity_result, integrity_result, context_result, quality_result = await asyncio.gather(
            identity_task,
            integrity_task,
            context_task,
            quality_task,
            return_exceptions=True,
        )

        layer_results: Dict[str, LayerResult] = {}
        layer_results["identity"] = self._safe_result(identity_result, "identity")
        layer_results["integrity"] = self._safe_result(integrity_result, "integrity")
        layer_results["context"] = self._safe_result(context_result, "context")
        layer_results["quality"] = self._safe_result(quality_result, "quality")

        if requested and requested != {"identity", "integrity", "context", "quality", "ai"}:
            layer_results = {name: result for name, result in layer_results.items() if name in requested}

        signals = self._merge_signals(layer_results)

        if not requested or "ai" in requested:
            try:
                ai_result = await self.ai_layer.evaluate(signals)
                layer_results["ai"] = ai_result
            except Exception as exc:
                layer_results["ai"] = LayerResult(
                    score_delta=0,
                    signals={},
                    apis_called=["rule_engine"],
                    latency_ms=0,
                    error=f"AI layer failed: {exc}",
                )

        score, weighted_deltas = compute_score(layer_results, request.use_case)
        confidence = confidence_from_layers(layer_results)
        ttl_seconds = ttl_for_use_case(request.use_case)
        badge = badge_for_score(score)

        for layer_name, weighted_delta in weighted_deltas.items():
            layer_results[layer_name].signals["weighted_delta"] = weighted_delta

        return TrustCallResponse(
            request_id=request_id_value,
            phone_number=request.phone_number,
            badge=badge,
            composite_score=score,
            layer_results=layer_results,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc),
            ttl_seconds=ttl_seconds,
        )

    @staticmethod
    def _safe_result(result: object, layer_name: str) -> LayerResult:
        if isinstance(result, LayerResult):
            return result
        if isinstance(result, Exception):
            return LayerResult(
                score_delta=0,
                signals={},
                apis_called=[layer_name],
                latency_ms=0,
                error=f"{layer_name} layer failed: {result}",
            )

        return LayerResult(
            score_delta=0,
            signals={},
            apis_called=[layer_name],
            latency_ms=0,
            error=f"{layer_name} layer returned unknown result type",
        )

    @staticmethod
    def _merge_signals(layer_results: Dict[str, LayerResult]) -> Dict[str, object]:
        merged: Dict[str, object] = {}
        for layer_result in layer_results.values():
            merged.update(layer_result.signals)
        return merged
