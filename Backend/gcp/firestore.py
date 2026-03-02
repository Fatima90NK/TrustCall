from datetime import datetime, timezone
from typing import Any

try:
    from google.cloud import firestore
except Exception:
    firestore = None


def _client() -> Any:
    if firestore is None:
        return None
    try:
        return firestore.Client()
    except Exception:
        return None


def save_handshake(request_id: str, payload: dict[str, Any]) -> None:
    client = _client()
    if client is None:
        return

    record = {
        **payload,
        "request_id": request_id,
        "created_at": datetime.now(timezone.utc),
    }
    client.collection("trust_handshakes").document(request_id).set(record)


def get_handshake(request_id: str) -> dict[str, Any] | None:
    client = _client()
    if client is None:
        return None

    doc = client.collection("trust_handshakes").document(request_id).get()
    if not doc.exists:
        return None

    data = doc.to_dict() or {}
    data["request_id"] = request_id
    return data
