from .client import NokiaClient


class CallForwardingAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def check(self, phone_number: str) -> dict | None:
        params = {"phoneNumber": phone_number}
        return await self.client.request("GET", "/call-forwarding/v0/check", params=params)
