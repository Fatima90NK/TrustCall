from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class LayerResult(BaseModel):
    score_delta: int = 0
    signals: dict[str, Any] = Field(default_factory=dict)
    apis_called: list[str] = Field(default_factory=list)
    latency_ms: int = 0
    error: str | None = None


class TrustCallResponse(BaseModel):
    request_id: str
    phone_number: str
    badge: Literal["TRUSTED", "CAUTION", "UNTRUSTED"]
    composite_score: int = Field(ge=0, le=100)
    layer_results: dict[str, LayerResult] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ttl_seconds: int = Field(ge=0)
