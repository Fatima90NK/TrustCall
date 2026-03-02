import os
from typing import Dict, Optional, Tuple, Union

from .client import NokiaClient


class NumberVerificationAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def verify(self, phone_number: str) -> dict | None:
        payload = {
            "phoneNumber": phone_number,
        }
        params, headers = self._authorization_context()

        if self.client.is_rapidapi_mode:
            result = await self.client.request(
                "POST",
                "/passthrough/camara/v1/number-verification/number-verification/v0/verify",
                json=payload,
                params=params,
                extra_headers=headers,
            )
            return self._normalize_verify_result(result)

        paths = [
            "/passthrough/camara/v1/number-verification/number-verification/v0/verify",
            "/number-verification/v0/verify",
            "/number-verification/v1/verify",
            "/number-verification/verify/v1",
            "/number-verification/verify/v0",
        ]
        result = await self.client.request_first(
            "POST",
            paths,
            json=payload,
            params=params,
            extra_headers=headers,
        )
        return self._normalize_verify_result(result)

    async def verify_detailed(self, phone_number: str) -> dict:
        payload = {
            "phoneNumber": phone_number,
        }
        params, headers = self._authorization_context()

        if self.client.is_rapidapi_mode:
            detailed = await self.client.request_detailed(
                "POST",
                "/passthrough/camara/v1/number-verification/number-verification/v0/verify",
                json=payload,
                params=params,
                extra_headers=headers,
            )
            if detailed.get("ok"):
                detailed["data"] = self._normalize_verify_result(detailed.get("data"))
            return detailed

        paths = [
            "/passthrough/camara/v1/number-verification/number-verification/v0/verify",
            "/number-verification/v0/verify",
            "/number-verification/v1/verify",
            "/number-verification/verify/v1",
            "/number-verification/verify/v0",
        ]
        detailed = await self.client.request_first_detailed(
            "POST",
            paths,
            json=payload,
            params=params,
            extra_headers=headers,
        )

        if detailed.get("ok"):
            detailed["data"] = self._normalize_verify_result(detailed.get("data"))

        return detailed

    def _authorization_context(self) -> Tuple[Optional[Dict], Optional[Dict]]:
        if not self.client.is_rapidapi_mode:
            return None, None

        bearer_token = os.getenv("NUMBER_VERIFICATION_BEARER_TOKEN")
        fast_code = os.getenv("NUMBER_VERIFICATION_CODE")
        fast_state = os.getenv("NUMBER_VERIFICATION_STATE")

        if bearer_token:
            return None, {"Authorization": f"Bearer {bearer_token}"}

        if fast_code and fast_state:
            return {"code": fast_code, "state": fast_state}, None

        return None, None

    @staticmethod
    def _normalize_verify_result(result: Union[Dict, bool, None]) -> Optional[Dict]:
        if isinstance(result, dict):
            return result
        if isinstance(result, bool):
            return {"devicePhoneNumberVerified": result}
        return None
