from uuid import uuid4

from fastapi import APIRouter, Depends

from api.middleware.auth import require_api_key
from api.models.request import TrustCallRequest
from api.models.response import LayerResult, TrustCallResponse

router = APIRouter(prefix="/v1", tags=["trust"])


@router.post("/trust-handshake", response_model=TrustCallResponse)
async def trust_handshake(
    payload: TrustCallRequest,
    _: None = Depends(require_api_key),
) -> TrustCallResponse:
    request_id = str(uuid4())

    return TrustCallResponse(
        request_id=request_id,
        phone_number=payload.phone_number,
        badge="CAUTION",
        composite_score=50,
        layer_results={
            "foundation": LayerResult(
                score_delta=0,
                signals={"phase": "phase_1_baseline"},
                apis_called=[],
                latency_ms=0,
            )
        },
        confidence=0.5,
        ttl_seconds=300,
    )
