from .client import NokiaClient


class SimSwapAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def check(self, phone_number: str, max_age: int = 240) -> dict | None:
        payload = {
            "phoneNumber": phone_number,
            "maxAge": max_age,
        }
        return await self.client.request("POST", "/sim-swap/v0/check", json=payload)
