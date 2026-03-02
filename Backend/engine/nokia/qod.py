from typing import Any

from .client import NokiaClient


class QoDAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def create_session(
        self,
        phone_number: str,
        ipv4_address: str,
        qos_profile: str = "QOS_E",
    ) -> dict[str, Any] | None:
        payload = {
            "device": {"phoneNumber": phone_number},
            "applicationServer": {"ipv4Address": ipv4_address},
            "qosProfile": qos_profile,
        }
        return await self.client.request("POST", "/qos-sessions/v0/sessions", json=payload)
