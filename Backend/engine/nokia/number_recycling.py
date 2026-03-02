from .client import NokiaClient


class NumberRecyclingAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def check(self, phone_number: str, max_age: int = 720) -> dict | None:
        payload = {
            "phoneNumber": phone_number,
            "maxAge": max_age,
        }
        return await self.client.request("POST", "/number-recycling/v0/check", json=payload)
