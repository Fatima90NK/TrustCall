from datetime import datetime, timedelta, timezone

from .client import NokiaClient


class NumberRecyclingAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def check(self, phone_number: str, max_age: int = 720) -> dict | None:
        payload = self._build_payload(phone_number=phone_number, max_age=max_age)
        paths = [
            "/passthrough/camara/v1/number-recycling/number-recycling/v0.2/check",
            "/number-recycling/v0/check",
            "/number-recycling/v1/check",
        ]
        return await self.client.request_first("POST", paths, json=payload)

    async def check_detailed(self, phone_number: str, max_age: int = 720) -> dict:
        payload = self._build_payload(phone_number=phone_number, max_age=max_age)
        paths = [
            "/passthrough/camara/v1/number-recycling/number-recycling/v0.2/check",
            "/number-recycling/v0/check",
            "/number-recycling/v1/check",
        ]
        return await self.client.request_first_detailed("POST", paths, json=payload)

    def _build_payload(self, phone_number: str, max_age: int) -> dict:
        if self.client.is_rapidapi_mode:
            specified_date = (datetime.now(timezone.utc) - timedelta(hours=max_age)).date().isoformat()
            return {
                "phoneNumber": phone_number,
                "specifiedDate": specified_date,
            }

        return {
            "phoneNumber": phone_number,
            "maxAge": max_age,
        }
