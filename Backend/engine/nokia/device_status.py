from .client import NokiaClient


class DeviceStatusAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def connectivity(self, phone_number: str) -> dict | None:
        payload = {
            "device": {"phoneNumber": phone_number},
        }
        paths = [
            "/device-status/v0/connectivity",
            "/device-status/device-roaming-status/v1/retrieve",
            "/device-status/v1/connectivity",
        ]
        return await self.client.request_first("POST", paths, json=payload)

    async def connectivity_detailed(self, phone_number: str) -> dict:
        payload = {
            "device": {"phoneNumber": phone_number},
        }
        paths = [
            "/device-status/v0/connectivity",
            "/device-status/device-roaming-status/v1/retrieve",
            "/device-status/v1/connectivity",
        ]
        return await self.client.request_first_detailed("POST", paths, json=payload)
