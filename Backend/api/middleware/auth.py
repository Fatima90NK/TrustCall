from fastapi import Header, HTTPException, status

from gcp.secrets import get_secret


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected_api_key = get_secret("trustcall/api-key")

    if not expected_api_key:
        expected_api_key = get_secret("TRUSTCALL_API_KEY")

    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server API key is not configured.",
        )

    if x_api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
