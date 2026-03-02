from typing import Any

from pydantic import BaseModel, Field


class LocationClaim(BaseModel):
    latitude: float
    longitude: float
    radius_meters: int = Field(default=2000, ge=1)


class KYCData(BaseModel):
    given_name: str | None = None
    family_name: str | None = None
    id_document: str | None = None
    address: dict[str, Any] | None = None
    age_threshold: int | None = Field(default=None, ge=0)


class TrustCallRequest(BaseModel):
    phone_number: str
    caller_name: str | None = None
    caller_ip: str | None = None
    claimed_location: LocationClaim | None = None
    kyc_data: KYCData | None = None
    use_case: str = "generic"
    requested_layers: list[str] = Field(
        default_factory=lambda: ["identity", "integrity", "context", "quality", "ai"]
    )
