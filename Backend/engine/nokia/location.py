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
        paths = [
            "/device-location/v0/retrieve",
            "/location-retrieval/v0/retrieve",
        ]
        return await self.client.request_first("POST", paths, json=payload)

    async def retrieve_detailed(self, phone_number: str, max_age: int = 60) -> Dict[str, Any]:
        payload = {
            "device": {"phoneNumber": phone_number},
            "maxAge": max_age,
        }
        paths = [
            "/device-location/v0/retrieve",
            "/location-retrieval/v0/retrieve",
        ]
        return await self.client.request_first_detailed("POST", paths, json=payload)

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
        paths = [
            "/device-location/v0/verify",
            "/location-verification/v0/verify",
        ]
        return await self.client.request_first("POST", paths, json=payload)

    async def verify_detailed(
        self,
        phone_number: str,
        area: Dict[str, Any],
        max_age: int = 60,
    ) -> Dict[str, Any]:
        payload = {
            "device": {"phoneNumber": phone_number},
            "area": area,
            "maxAge": max_age,
        }
        paths = [
            "/device-location/v0/verify",
            "/location-verification/v0/verify",
        ]
        return await self.client.request_first_detailed("POST", paths, json=payload)

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
        paths = [
            "/geofencing/v0/subscriptions",
            "/geofencing/v1/subscriptions",
        ]
        return await self.client.request_first("POST", paths, json=payload)
