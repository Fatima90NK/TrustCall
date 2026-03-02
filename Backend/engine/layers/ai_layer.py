import time
from typing import Any, Dict

from api.models.response import LayerResult


class AILayer:
    async def evaluate(self, all_signals: Dict[str, Any]) -> LayerResult:
        started = time.perf_counter()
        apis_called = ["rule_engine"]

        red_flags = 0
        green_flags = 0

        if all_signals.get("sim_swapped"):
            red_flags += 1
        if all_signals.get("device_swapped"):
            red_flags += 1
        if all_signals.get("number_recycled"):
            red_flags += 1
        if all_signals.get("call_forwarding_active"):
            red_flags += 1
        if all_signals.get("device_phone_number_verified"):
            green_flags += 1
        if all_signals.get("location_verification_result") == "TRUE":
            green_flags += 1
        if all_signals.get("connectivity_status") == "CONNECTED_DATA":
            green_flags += 1

        if red_flags >= 2:
            risk_label = "high"
            score_delta = -15
        elif green_flags >= 3 and red_flags == 0:
            risk_label = "low"
            score_delta = 10
        else:
            risk_label = "medium"
            score_delta = 0

        latency_ms = int((time.perf_counter() - started) * 1000)
        return LayerResult(
            score_delta=score_delta,
            signals={
                "risk_label": risk_label,
                "red_flags": red_flags,
                "green_flags": green_flags,
            },
            apis_called=apis_called,
            latency_ms=latency_ms,
        )
