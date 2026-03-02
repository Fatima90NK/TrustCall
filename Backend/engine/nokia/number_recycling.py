from .client import NokiaClient


class NumberRecyclingAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def check(self, phone_number: str, max_age: int = 720) -> dict | None:
        payload = {
            "phoneNumber": phone_number,
            "maxAge": max_age,
        }
        paths = [
            "/number-recycling/v0/check",
            "/number-recycling/v1/check",
        ]
        return await self.client.request_first("POST", paths, json=payload)

    async def check_detailed(self, phone_number: str, max_age: int = 720) -> dict:
        payload = {
            "phoneNumber": phone_number,
            "maxAge": max_age,
        }
        paths = [
            "/number-recycling/v0/check",
            "/number-recycling/v1/check",
        ]
        return await self.client.request_first_detailed("POST", paths, json=payload)
