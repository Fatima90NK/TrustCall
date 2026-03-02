from .client import NokiaClient


class NumberVerificationAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def verify(self, phone_number: str) -> dict | None:
        payload = {
            "phoneNumber": phone_number,
        }
        return await self.client.request("POST", "/number-verification/v0/verify", json=payload)
