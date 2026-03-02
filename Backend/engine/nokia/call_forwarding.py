from .client import NokiaClient


class CallForwardingAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def check(self, phone_number: str) -> dict | None:
        params = {"phoneNumber": phone_number}
        paths = [
            "/call-forwarding/v0/check",
            "/call-forwarding/v1/check",
            "/call-forwarding-unconditional-status/v1/retrieve",
        ]
        return await self.client.request_first("GET", paths, params=params)

    async def check_detailed(self, phone_number: str) -> dict:
        params = {"phoneNumber": phone_number}
        paths = [
            "/call-forwarding/v0/check",
            "/call-forwarding/v1/check",
            "/call-forwarding-unconditional-status/v1/retrieve",
        ]
        return await self.client.request_first_detailed("GET", paths, params=params)
