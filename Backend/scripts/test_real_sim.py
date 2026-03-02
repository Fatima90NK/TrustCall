import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, Optional
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from engine.layers.utils import normalize_phone_number
from engine.nokia.call_forwarding import CallForwardingAPI
from engine.nokia.client import NokiaClient
from engine.nokia.device_status import DeviceStatusAPI
from engine.nokia.kyc import KYCAPI
from engine.nokia.location import LocationAPI
from engine.nokia.number_recycling import NumberRecyclingAPI
from engine.nokia.number_verification import NumberVerificationAPI
from engine.nokia.sim_swap import SimSwapAPI


def _pretty(data: Optional[Dict[str, Any]]) -> str:
    return json.dumps(data or {}, indent=2, ensure_ascii=False)


async def run_smoke_test(phone_number: str, latitude: Optional[float], longitude: Optional[float]) -> None:
    client = NokiaClient()

    normalized = normalize_phone_number(phone_number)
    if not normalized:
        raise ValueError("Invalid phone number. Use E.164 format like +34612345678.")

    print(f"Using phone number: {normalized}")

    sim_swap_api = SimSwapAPI(client)
    number_verification_api = NumberVerificationAPI(client)
    number_recycling_api = NumberRecyclingAPI(client)
    call_forwarding_api = CallForwardingAPI(client)
    device_status_api = DeviceStatusAPI(client)
    location_api = LocationAPI(client)
    kyc_api = KYCAPI(client)

    checks = [
        ("number_verification", number_verification_api.verify_detailed(normalized)),
        ("sim_swap", sim_swap_api.check_detailed(normalized, max_age=240)),
        (
            "device_swap",
            client.request_first_detailed(
                "POST",
                [
                    "/passthrough/camara/v1/device-swap/device-swap/v1/check",
                    "/device-swap/v1/check",
                    "/device-swap/v0/check",
                ],
                json={"phoneNumber": normalized, "maxAge": 240},
            ),
        ),
        ("number_recycling", number_recycling_api.check_detailed(normalized, max_age=720)),
        ("call_forwarding", call_forwarding_api.check_detailed(normalized)),
        ("device_status", device_status_api.connectivity_detailed(normalized)),
        ("kyc_tenure", kyc_api.tenure_detailed(normalized)),
        ("location_retrieve", location_api.retrieve_detailed(normalized, max_age=60)),
    ]

    app_ipv4 = os.getenv("TRUSTCALL_APP_IPV4")
    if app_ipv4:
        checks.append(
            (
                "qod",
                client.request_detailed(
                    "POST",
                    "/qos-sessions/v0/sessions",
                    json={
                        "device": {"phoneNumber": normalized},
                        "applicationServer": {"ipv4Address": app_ipv4},
                        "qosProfile": "QOS_E",
                    },
                ),
            )
        )
    else:
        print("Skipping qod check: TRUSTCALL_APP_IPV4 not set")

    if latitude is not None and longitude is not None:
        area = {
            "areaType": "CIRCLE",
            "center": {"latitude": latitude, "longitude": longitude},
            "radius": 2000,
        }
        checks.append(("location_verify", location_api.verify_detailed(normalized, area=area, max_age=60)))
    else:
        print("Skipping location_verify: no --latitude/--longitude provided")

    results = await asyncio.gather(*(coro for _, coro in checks), return_exceptions=True)

    print("\n=== Nokia API Smoke Test Results ===")
    success_count = 0
    for (name, _), result in zip(checks, results):
        if isinstance(result, Exception):
            print(f"\n[{name}] ERROR: {result}")
            continue

        if not isinstance(result, dict):
            print(f"\n[{name}] FAILED (unexpected response type: {type(result).__name__})")
            continue

        status_code = result.get("status_code")
        path = result.get("path")
        error = result.get("error")
        text = result.get("text")
        data = result.get("data")

        ok = bool(result.get("ok"))
        if ok:
            success_count += 1
            print(f"\n[{name}] OK")
        else:
            print(f"\n[{name}] FAILED")

        print(f"  path: {path}")
        print(f"  status: {status_code}")
        if error:
            print(f"  error: {error}")

        if isinstance(data, dict) and data:
            print(_pretty(data))
        elif isinstance(text, str) and text:
            print(f"  body: {text[:500]}")

    print(f"\nSummary: {success_count}/{len(checks)} checks returned data")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run real-SIM Nokia API smoke tests.")
    parser.add_argument("--phone", required=True, help="Phone number in E.164, e.g. +34612345678")
    parser.add_argument("--latitude", type=float, required=False, help="Claimed latitude for location_verify")
    parser.add_argument("--longitude", type=float, required=False, help="Claimed longitude for location_verify")
    return parser.parse_args()


if __name__ == "__main__":
    load_dotenv()
    args = parse_args()
    asyncio.run(run_smoke_test(args.phone, args.latitude, args.longitude))
