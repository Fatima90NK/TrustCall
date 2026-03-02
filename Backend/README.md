# TrustCall Backend (Current Handoff)

Backend is runnable and actively integrated with Nokia Network as Code via RapidAPI. The trust-handshake workflow is working end-to-end with graceful degradation and real-number testing.

## Implemented Scope

- FastAPI backend, models, middleware, Dockerfile, env loading
- Nokia client with RapidAPI mode + OAuth fallback
- Layered trust engine (identity, integrity, context, quality, ai)
- Weighted scoring, badge assignment, TTL policy
- Routes:
  - `POST /v1/trust-handshake`
  - `GET /v1/trust-handshake/{request_id}`
- Firestore read/write integration for handshake persistence
- Real SIM smoke test and local handshake test scripts

## Live API Coverage

### Working now (RapidAPI)

- `POST /passthrough/camara/v1/sim-swap/sim-swap/v0/check`
- `POST /passthrough/camara/v1/device-swap/device-swap/v1/check`
- `POST /passthrough/camara/v1/number-recycling/number-recycling/v0.2/check`
- `POST /passthrough/camara/v1/call-forwarding-signal/call-forwarding-signal/v0.3/unconditional-call-forwardings`
- `POST /device-status/v0/connectivity`
- `POST /location-retrieval/v0/retrieve`

### Conditionally working

- `POST /passthrough/camara/v1/kyc-tenure/kyc-tenure/v0.1/check-tenure`
  - Works on simulator numbers with matching scenario date (e.g. `2023-07-03`)
  - Real number may return `400` if tenure date does not match operator scenario

### Requires consent flow

- `POST /passthrough/camara/v1/number-verification/number-verification/v0/verify`
  - Currently returns `401 Authorization header is missing` unless consent token/code is provided
  - Needs either:
    - `Authorization: Bearer <single-use-access-token>`
    - or fast flow `?code=<code>&state=<state>`

## Scoring Behavior (Current)

- Unavailable identity/context checks are neutralized (score delta `0`) instead of penalized.
- High-confidence negative integrity signals still apply penalties.
- This keeps workflow usable while Number Verification and some tenure scenarios are not fully configured.

## Latest Handshake Snapshot (real number)

Input: `+34640032379`

- `badge`: `UNTRUSTED`
- `composite_score`: `0`
- Layer deltas:
  - `identity`: `0` (neutral; number verification not authorized)
  - `integrity`: `-50` (`device_swapped=true`, `call_forwarding_active=true`)
  - `context`: `0` (neutral; tenure unavailable)
  - `quality`: `+10` (`CONNECTED_DATA`)
  - `ai`: `-15` (`risk_label=high`)

## Required Local Environment

Create `Backend/.env`:

```bash
# RapidAPI mode
RAPIDAPI_KEY=<your-rapidapi-key>
RAPIDAPI_HOST=network-as-code.nokia.rapidapi.com
RAPIDAPI_BASE_URL=https://network-as-code.p-eu.rapidapi.com

# TrustCall local API auth
TRUSTCALL_API_KEY=<your-local-key>

# Optional runtime
NOKIA_REQUEST_TIMEOUT=10
TRUSTCALL_APP_IPV4=<public-ip-for-qod-if-needed>

# Number Verification (consent-based, optional)
NUMBER_VERIFICATION_BEARER_TOKEN=<single-use-token>
NUMBER_VERIFICATION_CODE=<fast-flow-code>
NUMBER_VERIFICATION_STATE=<fast-flow-state>

# KYC tenure scenario override (optional)
KYC_TENURE_DATE=2023-07-03
```

## Run Locally

```bash
cd Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Test Commands

Smoke test:

```bash
python scripts/test_real_sim.py --phone "+34640032379"
```

Handshake test:

```bash
TRUSTCALL_API_KEY=<TRUSTCALL_API_KEY> TEST_PHONE_E164=+34640032379 ./scripts/test_handshake_local.sh
```

## Deployment Notes

- ASGI entrypoint: `main:app`
- Container port: `8080` (Dockerfile)
- Secrets/env can be injected without code changes
- Firestore persistence is already wired for handshake responses

## Next Work

- Add Number Verification consent helper endpoints (`state`, callback `code` capture)
- Add capability flags so unavailable APIs are explicitly skipped in layer execution
- Add automated tests for layer logic and trust engine orchestration
