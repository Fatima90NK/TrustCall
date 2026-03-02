from .client import NokiaClient


class NumberVerificationAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def verify(self, phone_number: str) -> dict | None:
        payload = {
            "phoneNumber": phone_number,
        }
        paths = [
            "/number-verification/v0/verify",
            "/number-verification/v1/verify",
            "/number-verification/verify/v1",
            "/number-verification/verify/v0",
        ]
        return await self.client.request_first("POST", paths, json=payload)

    async def verify_detailed(self, phone_number: str) -> dict:
        payload = {
            "phoneNumber": phone_number,
        }
        paths = [
            "/number-verification/v0/verify",
            "/number-verification/v1/verify",
            "/number-verification/verify/v1",
            "/number-verification/verify/v0",
        ]
        return await self.client.request_first_detailed("POST", paths, json=payload)
