import time
from typing import Any, Dict, Optional

from api.models.response import LayerResult
from engine.nokia.call_forwarding import CallForwardingAPI
from engine.nokia.client import NokiaClient
from engine.nokia.number_recycling import NumberRecyclingAPI
from engine.nokia.sim_swap import SimSwapAPI

from .utils import normalize_phone_number


class IntegrityLayer:
    def __init__(self, client: Optional[NokiaClient] = None) -> None:
        self.client = client or NokiaClient()
        self.sim_swap_api = SimSwapAPI(self.client)
        self.number_recycling_api = NumberRecyclingAPI(self.client)
        self.call_forwarding_api = CallForwardingAPI(self.client)

    async def evaluate(self, phone_number: str) -> LayerResult:
        started = time.perf_counter()
        signals: Dict[str, Any] = {}
        apis_called = ["sim_swap", "device_swap", "number_recycling", "call_forwarding"]
        score_delta = 0

        normalized = normalize_phone_number(phone_number)
        if not normalized:
            latency_ms = int((time.perf_counter() - started) * 1000)
            return LayerResult(
                score_delta=0,
                signals={"phone_number_valid": False},
                apis_called=apis_called,
                latency_ms=latency_ms,
                error="Invalid phone number format. Expected E.164-compatible number.",
            )

        signals["phone_number"] = normalized
        signals["phone_number_valid"] = True

        try:
            sim_swap = await self.sim_swap_api.check(normalized)
            sim_swapped = bool((sim_swap or {}).get("swapped", False))
            signals["sim_swapped"] = sim_swapped
            if sim_swapped:
                score_delta -= 40

            device_swap = await self.client.request(
                "POST",
                "/device-swap/v0/check",
                json={"phoneNumber": normalized, "maxAge": 240},
            )
            device_swapped = bool((device_swap or {}).get("swapped", False))
            signals["device_swapped"] = device_swapped
            if device_swapped:
                score_delta -= 30

            recycling = await self.number_recycling_api.check(normalized, max_age=720)
            recycled = bool((recycling or {}).get("recycled", False))
            signals["number_recycled"] = recycled
            if recycled:
                score_delta -= 35

            forwarding = await self.call_forwarding_api.check(normalized)
            forwarding_active = bool((forwarding or {}).get("active", False))
            signals["call_forwarding_active"] = forwarding_active
            if forwarding_active:
                score_delta -= 20
        except Exception as exc:
            latency_ms = int((time.perf_counter() - started) * 1000)
            return LayerResult(
                score_delta=score_delta,
                signals=signals,
                apis_called=apis_called,
                latency_ms=latency_ms,
                error=str(exc),
            )

        latency_ms = int((time.perf_counter() - started) * 1000)
        return LayerResult(
            score_delta=score_delta,
            signals=signals,
            apis_called=apis_called,
            latency_ms=latency_ms,
        )
