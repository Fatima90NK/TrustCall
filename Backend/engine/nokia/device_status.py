from .client import NokiaClient


class DeviceStatusAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def connectivity(self, phone_number: str) -> dict | None:
        payload = {
            "device": {"phoneNumber": phone_number},
        }
        return await self.client.request("POST", "/device-status/v0/connectivity", json=payload)
