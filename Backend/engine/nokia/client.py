import asyncio
import os
import time
from typing import Any, Dict, Optional, Tuple

import httpx

from gcp.secrets import get_secret


class NokiaClient:
    def __init__(self, timeout_seconds: Optional[float] = None) -> None:
        self.base_url = (
            get_secret("nokia/base-url")
            or get_secret("NOKIA_BASE_URL")
            or ""
        ).rstrip("/")
        self.client_id = get_secret("nokia/client-id") or get_secret("NOKIA_CLIENT_ID")
        self.client_secret = get_secret("nokia/client-secret") or get_secret("NOKIA_CLIENT_SECRET")

        self.timeout_seconds = timeout_seconds or float(os.getenv("NOKIA_REQUEST_TIMEOUT", "5"))

        self._token: Optional[str] = None
        self._token_expires_at: float = 0
        self._token_lock = asyncio.Lock()

    async def _fetch_access_token(self) -> Tuple[Optional[str], int]:
        if not self.base_url or not self.client_id or not self.client_secret:
            return None, 0

        token_url = f"{self.base_url}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(token_url, data=payload)
                response.raise_for_status()
                data = response.json()

            access_token = data.get("access_token")
            expires_in = int(data.get("expires_in", 3600))
            return access_token, expires_in
        except Exception:
            return None, 0

    async def _get_access_token(self) -> Optional[str]:
        now = time.time()
        if self._token and now < self._token_expires_at:
            return self._token

        async with self._token_lock:
            now = time.time()
            if self._token and now < self._token_expires_at:
                return self._token

            token, expires_in = await self._fetch_access_token()
            if not token:
                return None

            refresh_buffer_seconds = 300
            safe_expires_in = max(60, expires_in - refresh_buffer_seconds)
            self._token = token
            self._token_expires_at = time.time() + safe_expires_in
            return self._token

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[float] = None,
        retries: int = 3,
    ) -> Optional[Dict[str, Any]]:
        if not self.base_url:
            return None

        token = await self._get_access_token()
        if not token:
            return None

        url = f"{self.base_url}/{path.lstrip('/')}"
        timeout = timeout_seconds or self.timeout_seconds

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        for attempt in range(1, retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.request(
                        method=method.upper(),
                        url=url,
                        headers=headers,
                        json=json,
                        params=params,
                    )

                if response.status_code == 401 and attempt < retries:
                    self._token = None
                    self._token_expires_at = 0
                    token = await self._get_access_token()
                    if not token:
                        return None
                    headers["Authorization"] = f"Bearer {token}"
                    await asyncio.sleep(0.2 * (2 ** (attempt - 1)))
                    continue

                response.raise_for_status()
                if not response.text:
                    return {}
                return response.json()
            except Exception:
                if attempt == retries:
                    return None
                await asyncio.sleep(0.2 * (2 ** (attempt - 1)))

        return None
