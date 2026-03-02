# TrustCall Backend (Handoff)

This backend is now runnable locally and ready for parallel deployment work while API coverage is expanded.

## Current Status

Implemented so far:
- Phase 1: FastAPI app foundation, models, auth middleware, env loading, Dockerfile
- Phase 2: Nokia client + endpoint wrappers
- Phase 3: Layer evaluators (identity, integrity, context, quality, ai)
- Phase 4: Scoring + trust engine orchestration
- Phase 5: `/v1/trust-handshake` and `/v1/trust-handshake/{request_id}`
- RapidAPI support mode in Nokia client (`RAPIDAPI_KEY`)
- Real-SIM smoke test script with per-endpoint diagnostics

## Known RapidAPI Test Results (current product set)

Using test number `+99999991000` with current credentials:
- Working:
  - `POST /device-status/v0/connectivity`
  - `POST /location-retrieval/v0/retrieve`
- Not currently available in this RapidAPI subscription (404 in tests):
  - number verification
  - sim swap
  - device swap
  - number recycling
  - call forwarding
  - kyc tenure

Server still runs and handshake works with graceful degradation when some APIs are unavailable.

## Required Local Environment

Create `Backend/.env`:

```bash
# RapidAPI mode (recommended for local right now)
RAPIDAPI_KEY=<your-rapidapi-key>
RAPIDAPI_HOST=network-as-code.nokia.rapidapi.com
RAPIDAPI_BASE_URL=https://network-as-code.p-eu.rapidapi.com

# Local API protection for TrustCall routes
TRUSTCALL_API_KEY=<your-local-key>

# Optional
NOKIA_REQUEST_TIMEOUT=10
TRUSTCALL_APP_IPV4=<public-ip-for-qod-if-needed>
```

## How to Run Server

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

## Test Case (Smoke Test)

Run real-number/sandbox diagnostics:

```bash
python scripts/test_real_sim.py --phone "+99999991000"
```

Optional location verify:

```bash
python scripts/test_real_sim.py --phone "+99999991000" --latitude <lat> --longitude <lng>
```

## API Test Case (Handshake)

```bash
curl -X POST "http://127.0.0.1:8000/v1/trust-handshake" \
  -H "Content-Type: application/json" \
  -H "x-api-key: <TRUSTCALL_API_KEY>" \
  -d '{
    "phone_number": "+99999991000",
    "use_case": "generic",
    "requested_layers": ["identity", "integrity", "context", "quality", "ai"]
  }'
```

Example expected behavior right now:
- returns `200`
- includes `badge`, `composite_score`, and `layer_results`
- unavailable APIs degrade gracefully instead of crashing

## Notes for Deployment Teammate

- Service entrypoint: `main:app`
- Container target port: `8080` in `Dockerfile`
- Secrets/env can be wired without changing code
- Firestore write/read is already integrated in handshake routes

## Next Backend Work (kept for now)

- Map remaining wrappers to exact RapidAPI endpoints enabled in subscription
- Add per-API capability flags so unavailable products are automatically excluded from scoring
- Add unit tests + integration tests for engine/layers
