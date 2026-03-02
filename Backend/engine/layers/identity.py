import time
from typing import Any, Dict, Optional

from api.models.request import KYCData
from api.models.response import LayerResult
from engine.nokia.client import NokiaClient
from engine.nokia.kyc import KYCAPI
from engine.nokia.number_verification import NumberVerificationAPI

from .utils import normalize_phone_number


class IdentityLayer:
    def __init__(self, client: Optional[NokiaClient] = None) -> None:
        self.client = client or NokiaClient()
        self.number_verification_api = NumberVerificationAPI(self.client)
        self.kyc_api = KYCAPI(self.client)

    async def evaluate(self, phone_number: str, kyc_data: Optional[KYCData] = None) -> LayerResult:
        started = time.perf_counter()
        signals: Dict[str, Any] = {}
        apis_called = ["number_verification", "kyc_fill_in", "kyc_match"]
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
            verification = await self.number_verification_api.verify(normalized)
            verification_available = verification is not None
            verified = bool((verification or {}).get("devicePhoneNumberVerified", False))
            signals["number_verification_available"] = verification_available
            signals["device_phone_number_verified"] = verified
            if verified:
                score_delta += 15

            fill_result = await self.kyc_api.fill_in(normalized, ["name", "address"])
            signals["kyc_fill_in"] = fill_result or {}

            match_payload = kyc_data or KYCData()
            if fill_result:
                name_data = fill_result.get("name") or {}
                address_data = fill_result.get("address")

                if not match_payload.given_name:
                    match_payload.given_name = name_data.get("givenName")
                if not match_payload.family_name:
                    match_payload.family_name = name_data.get("familyName")
                if not match_payload.address and address_data:
                    match_payload.address = address_data

            kyc_match = await self.kyc_api.match(
                phone_number=normalized,
                id_document=match_payload.id_document,
                given_name=match_payload.given_name,
                family_name=match_payload.family_name,
                address=match_payload.address,
            )
            kyc_match_available = kyc_match is not None
            match_score = int((kyc_match or {}).get("matchScore", 0))
            signals["kyc_match_available"] = kyc_match_available
            signals["kyc_match_score"] = match_score

            if kyc_match_available:
                if match_score > 80:
                    score_delta += 15
                elif match_score >= 50:
                    score_delta += 5
                else:
                    score_delta -= 10
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
