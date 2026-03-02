from .client import NokiaClient


class CallForwardingAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def check(self, phone_number: str) -> dict | None:
        if self.client.is_rapidapi_mode:
            payload = {"phoneNumber": phone_number}
            paths = [
                "/passthrough/camara/v1/call-forwarding-signal/call-forwarding-signal/v0.3/unconditional-call-forwardings",
                "/passthrough/camara/v1/call-forwarding-signal/call-forwarding-signal/v0.3/call-forwardings",
                "/call-forwarding-signal/v0.3/unconditional-call-forwardings",
            ]
            return await self.client.request_first("POST", paths, json=payload)

        params = {"phoneNumber": phone_number}
        paths = [
            "/call-forwarding/v0/check",
            "/call-forwarding/v1/check",
            "/call-forwarding-unconditional-status/v1/retrieve",
        ]
        return await self.client.request_first("GET", paths, params=params)

    async def check_detailed(self, phone_number: str) -> dict:
        if self.client.is_rapidapi_mode:
            payload = {"phoneNumber": phone_number}
            paths = [
                "/passthrough/camara/v1/call-forwarding-signal/call-forwarding-signal/v0.3/unconditional-call-forwardings",
                "/passthrough/camara/v1/call-forwarding-signal/call-forwarding-signal/v0.3/call-forwardings",
                "/call-forwarding-signal/v0.3/unconditional-call-forwardings",
            ]
            return await self.client.request_first_detailed("POST", paths, json=payload)

        params = {"phoneNumber": phone_number}
        paths = [
            "/call-forwarding/v0/check",
            "/call-forwarding/v1/check",
            "/call-forwarding-unconditional-status/v1/retrieve",
        ]
        return await self.client.request_first_detailed("GET", paths, params=params)
