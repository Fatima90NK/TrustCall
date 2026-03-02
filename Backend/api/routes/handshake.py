from fastapi import APIRouter, Depends, HTTPException, status

from api.middleware.auth import require_api_key
from api.models.request import TrustCallRequest
from api.models.response import TrustCallResponse
from engine.trust_engine import TrustCallEngine
from gcp.firestore import get_handshake, save_handshake

router = APIRouter(prefix="/v1", tags=["trust"])
engine = TrustCallEngine()


@router.post("/trust-handshake", response_model=TrustCallResponse)
async def trust_handshake(
    payload: TrustCallRequest,
    _: None = Depends(require_api_key),
) -> TrustCallResponse:
    response = await engine.run(payload)
    save_handshake(response.request_id, response.model_dump(mode="python"))
    return response


@router.get("/trust-handshake/{request_id}", response_model=TrustCallResponse)
async def get_trust_handshake(
    request_id: str,
    _: None = Depends(require_api_key),
) -> TrustCallResponse:
    result = get_handshake(request_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Handshake request not found.",
        )

    return TrustCallResponse.model_validate(result)
