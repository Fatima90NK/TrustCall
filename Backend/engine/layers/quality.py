import os
import time
from typing import Any, Dict, Optional

from api.models.response import LayerResult
from engine.nokia.client import NokiaClient
from engine.nokia.device_status import DeviceStatusAPI
from engine.nokia.qod import QoDAPI

from .utils import normalize_phone_number


class QualityLayer:
    def __init__(self, client: Optional[NokiaClient] = None) -> None:
        self.client = client or NokiaClient()
        self.device_status_api = DeviceStatusAPI(self.client)
        self.qod_api = QoDAPI(self.client)

    async def evaluate(self, phone_number: str) -> LayerResult:
        started = time.perf_counter()
        signals: Dict[str, Any] = {}
        apis_called = ["device_status", "qod"]
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
            connectivity = await self.device_status_api.connectivity(normalized)
            status = (connectivity or {}).get(
                "connectivityStatus",
                (connectivity or {}).get("connectivity_status", "UNKNOWN"),
            )
            signals["connectivity_status"] = status

            if status == "CONNECTED_DATA":
                score_delta += 10
            elif status == "NOT_CONNECTED":
                score_delta -= 10

            qod_ipv4 = os.getenv("TRUSTCALL_APP_IPV4", "127.0.0.1")
            qos = await self.qod_api.create_session(normalized, ipv4_address=qod_ipv4)
            qos_status = (qos or {}).get("qosStatus", "UNAVAILABLE")
            signals["qod_status"] = qos_status
            if qos_status == "AVAILABLE":
                score_delta += 5
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
