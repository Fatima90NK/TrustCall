import time
from typing import Any, Dict, Optional

from api.models.request import LocationClaim
from api.models.response import LayerResult
from engine.nokia.client import NokiaClient
from engine.nokia.kyc import KYCAPI
from engine.nokia.location import LocationAPI

from .utils import normalize_phone_number


class ContextLayer:
    def __init__(self, client: Optional[NokiaClient] = None) -> None:
        self.client = client or NokiaClient()
        self.location_api = LocationAPI(self.client)
        self.kyc_api = KYCAPI(self.client)

    async def evaluate(
        self,
        phone_number: str,
        claimed_location: Optional[LocationClaim] = None,
    ) -> LayerResult:
        started = time.perf_counter()
        signals: Dict[str, Any] = {}
        apis_called = ["location_retrieval", "location_verification", "kyc_tenure"]
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
            retrieval = await self.location_api.retrieve(normalized, max_age=60)
            signals["location_retrieval"] = retrieval or {}

            if claimed_location:
                area = {
                    "areaType": "CIRCLE",
                    "center": {
                        "latitude": claimed_location.latitude,
                        "longitude": claimed_location.longitude,
                    },
                    "radius": claimed_location.radius_meters,
                }
                verification = await self.location_api.verify(normalized, area=area, max_age=60)
                result = (verification or {}).get("verificationResult", "UNKNOWN")
                signals["location_verification_result"] = result

                if result == "TRUE":
                    score_delta += 20
                elif result == "PARTIAL":
                    score_delta += 5
                elif result in {"FALSE", "UNKNOWN"}:
                    score_delta -= 20

            tenure = await self.kyc_api.tenure(normalized)
            tenure_available = tenure is not None
            tenure_months = int((tenure or {}).get("tenureMonths", 0))
            if tenure_months == 0 and "tenureDateCheck" in (tenure or {}):
                tenure_months = 24 if bool((tenure or {}).get("tenureDateCheck")) else 0
            signals["tenure_available"] = tenure_available
            signals["tenure_months"] = tenure_months

            if tenure_available:
                if tenure_months > 24:
                    score_delta += 10
                elif tenure_months < 3:
                    score_delta -= 5
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
