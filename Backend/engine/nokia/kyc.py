from typing import Any, Dict, List, Optional

from .client import NokiaClient


class KYCAPI:
    def __init__(self, client: NokiaClient) -> None:
        self.client = client

    async def match(
        self,
        phone_number: str,
        id_document: Optional[str] = None,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
        address: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        payload: Dict[str, Any] = {"phoneNumber": phone_number}
        if id_document:
            payload["idDocument"] = id_document
        if given_name or family_name:
            payload["name"] = {
                "givenName": given_name,
                "familyName": family_name,
            }
        if address:
            payload["address"] = address

        return await self.client.request("POST", "/kyc-match/v0/match", json=payload)

    async def verify_age(self, phone_number: str, age_threshold: int = 18) -> Optional[Dict[str, Any]]:
        payload = {
            "phoneNumber": phone_number,
            "ageThreshold": age_threshold,
        }
        return await self.client.request("POST", "/kyc-age-verification/v0/verify", json=payload)

    async def tenure(self, phone_number: str) -> Optional[Dict[str, Any]]:
        params = {"phoneNumber": phone_number}
        paths = [
            "/kyc-tenure/v0/check",
            "/kyc/tenure/v0/check",
            "/kyc-tenure/v1/check",
        ]
        return await self.client.request_first("GET", paths, params=params)

    async def tenure_detailed(self, phone_number: str) -> Dict[str, Any]:
        params = {"phoneNumber": phone_number}
        paths = [
            "/kyc-tenure/v0/check",
            "/kyc/tenure/v0/check",
            "/kyc-tenure/v1/check",
        ]
        return await self.client.request_first_detailed("GET", paths, params=params)

    async def fill_in(
        self,
        phone_number: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "phoneNumber": phone_number,
            "fields": fields or ["name", "address"],
        }
        return await self.client.request("POST", "/kyc-fill-in/v0/fill", json=payload)
