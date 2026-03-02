from .client import NokiaClient


class SimSwapAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def check(self, phone_number: str, max_age: int = 240) -> dict | None:
        payload = {
            "phoneNumber": phone_number,
            "maxAge": max_age,
        }
        paths = [
            "/passthrough/camara/v1/sim-swap/sim-swap/v0/check",
            "/sim-swap/v0/check",
            "/sim-swap/v1/check",
            "/sim-swap/v0/retrieve",
        ]
        return await self.client.request_first("POST", paths, json=payload)

    async def check_detailed(self, phone_number: str, max_age: int = 240) -> dict:
        payload = {
            "phoneNumber": phone_number,
            "maxAge": max_age,
        }
        paths = [
            "/passthrough/camara/v1/sim-swap/sim-swap/v0/check",
            "/sim-swap/v0/check",
            "/sim-swap/v1/check",
            "/sim-swap/v0/retrieve",
        ]
        return await self.client.request_first_detailed("POST", paths, json=payload)

    async def retrieve_swap_date(self, phone_number: str) -> dict | None:
        payload = {
            "phoneNumber": phone_number,
        }
        paths = [
            "/passthrough/camara/v1/sim-swap/sim-swap/v0/retrieve-date",
            "/sim-swap/v0/retrieve-date",
        ]
        return await self.client.request_first("POST", paths, json=payload)

    async def retrieve_swap_date_detailed(self, phone_number: str) -> dict:
        payload = {
            "phoneNumber": phone_number,
        }
        paths = [
            "/passthrough/camara/v1/sim-swap/sim-swap/v0/retrieve-date",
            "/sim-swap/v0/retrieve-date",
        ]
        return await self.client.request_first_detailed("POST", paths, json=payload)
