from typing import Any, Dict, Optional

from .client import NokiaClient


class LocationAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def retrieve(self, phone_number: str, max_age: int = 60) -> Optional[Dict[str, Any]]:
        payload = {
            "device": {"phoneNumber": phone_number},
            "maxAge": max_age,
        }
        return await self.client.request("POST", "/device-location/v0/retrieve", json=payload)

    async def verify(
        self,
        phone_number: str,
        area: Dict[str, Any],
        max_age: int = 60,
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "device": {"phoneNumber": phone_number},
            "area": area,
            "maxAge": max_age,
        }
        return await self.client.request("POST", "/device-location/v0/verify", json=payload)

    async def create_geofence_subscription(
        self,
        phone_number: str,
        area: Dict[str, Any],
        sink: str,
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "device": {"phoneNumber": phone_number},
            "area": area,
            "sink": sink,
        }
        return await self.client.request("POST", "/geofencing/v0/subscriptions", json=payload)
