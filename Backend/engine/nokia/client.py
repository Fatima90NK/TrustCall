import asyncio
import json as json_lib
import os
import time
from uuid import uuid4
from typing import Any, Dict, List, Optional, Tuple

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

        self.rapidapi_key = get_secret("RAPIDAPI_KEY")
        self.rapidapi_host = get_secret("RAPIDAPI_HOST") or os.getenv(
            "RAPIDAPI_HOST", "network-as-code.nokia.rapidapi.com"
        )
        self.rapidapi_base_url = (
            get_secret("RAPIDAPI_BASE_URL")
            or os.getenv("RAPIDAPI_BASE_URL", "https://network-as-code.p-eu.rapidapi.com")
        ).rstrip("/")

        if self.rapidapi_key and not self.base_url:
            self.base_url = self.rapidapi_base_url

        self.timeout_seconds = timeout_seconds or float(os.getenv("NOKIA_REQUEST_TIMEOUT", "5"))

        self._token: Optional[str] = None
        self._token_expires_at: float = 0
        self._token_lock = asyncio.Lock()

    @property
    def is_rapidapi_mode(self) -> bool:
        return bool(self.rapidapi_key)

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
        extra_headers: Optional[Dict[str, str]] = None,
        timeout_seconds: Optional[float] = None,
        retries: int = 3,
    ) -> Optional[Dict[str, Any]]:
        detailed = await self.request_detailed(
            method,
            path,
            json=json,
            params=params,
            extra_headers=extra_headers,
            timeout_seconds=timeout_seconds,
            retries=retries,
        )
        return detailed.get("data") if detailed.get("ok") else None

    async def request_detailed(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        timeout_seconds: Optional[float] = None,
        retries: int = 3,
    ) -> Dict[str, Any]:
        if not self.base_url:
            return {
                "ok": False,
                "path": path,
                "status_code": None,
                "data": None,
                "text": None,
                "error": "Missing Nokia base URL",
            }

        url = f"{self.base_url}/{path.lstrip('/')}"
        timeout = timeout_seconds or self.timeout_seconds

        use_rapidapi = bool(self.rapidapi_key)

        if use_rapidapi:
            headers = {
                "x-rapidapi-key": str(self.rapidapi_key),
                "x-rapidapi-host": str(self.rapidapi_host),
                "x-correlator": str(uuid4()),
                "Content-Type": "application/json",
            }
            token = None
        else:
            token = await self._get_access_token()
            if not token:
                return {
                    "ok": False,
                    "path": path,
                    "status_code": None,
                    "data": None,
                    "text": None,
                    "error": "OAuth token fetch failed",
                }
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

        if extra_headers:
            headers.update(extra_headers)

        last_error: Optional[str] = None
        last_status: Optional[int] = None
        last_text: Optional[str] = None

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

                last_status = response.status_code
                last_text = response.text

                if response.status_code == 401 and not use_rapidapi and attempt < retries:
                    self._token = None
                    self._token_expires_at = 0
                    token = await self._get_access_token()
                    if not token:
                        return {
                            "ok": False,
                            "path": path,
                            "status_code": response.status_code,
                            "data": None,
                            "text": response.text,
                            "error": "OAuth token refresh failed",
                        }
                    headers["Authorization"] = f"Bearer {token}"
                    await asyncio.sleep(0.2 * (2 ** (attempt - 1)))
                    continue

                if response.is_success:
                    if not response.text:
                        return {
                            "ok": True,
                            "path": path,
                            "status_code": response.status_code,
                            "data": {},
                            "text": "",
                            "error": None,
                        }

                    try:
                        data = response.json()
                    except json_lib.JSONDecodeError:
                        data = {"raw": response.text}

                    return {
                        "ok": True,
                        "path": path,
                        "status_code": response.status_code,
                        "data": data,
                        "text": response.text,
                        "error": None,
                    }

                last_error = f"HTTP {response.status_code}"
                if response.status_code < 500 and response.status_code != 429:
                    return {
                        "ok": False,
                        "path": path,
                        "status_code": response.status_code,
                        "data": None,
                        "text": response.text,
                        "error": last_error,
                    }
            except Exception as exc:
                last_error = str(exc)
                if attempt == retries:
                    return {
                        "ok": False,
                        "path": path,
                        "status_code": last_status,
                        "data": None,
                        "text": last_text,
                        "error": last_error,
                    }
                await asyncio.sleep(0.2 * (2 ** (attempt - 1)))

        return {
            "ok": False,
            "path": path,
            "status_code": last_status,
            "data": None,
            "text": last_text,
            "error": last_error or "Request failed",
        }

    async def request_first(
        self,
        method: str,
        paths: List[str],
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        timeout_seconds: Optional[float] = None,
        retries: int = 2,
    ) -> Optional[Dict[str, Any]]:
        detailed = await self.request_first_detailed(
            method,
            paths,
            json=json,
            params=params,
            extra_headers=extra_headers,
            timeout_seconds=timeout_seconds,
            retries=retries,
        )
        return detailed.get("data") if detailed.get("ok") else None

    async def request_first_detailed(
        self,
        method: str,
        paths: List[str],
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        timeout_seconds: Optional[float] = None,
        retries: int = 2,
    ) -> Dict[str, Any]:
        last_result: Dict[str, Any] = {
            "ok": False,
            "path": None,
            "status_code": None,
            "data": None,
            "text": None,
            "error": "No paths attempted",
        }

        for path in paths:
            result = await self.request_detailed(
                method,
                path,
                json=json,
                params=params,
                extra_headers=extra_headers,
                timeout_seconds=timeout_seconds,
                retries=retries,
            )
            if result.get("ok"):
                return result
            last_result = result

            status_code = result.get("status_code")
            if status_code == 403:
                return result
            if isinstance(status_code, int) and 400 <= status_code < 500 and status_code != 404:
                return result

        return last_result
