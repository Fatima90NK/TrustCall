# Real SIM API Test Checklist (Phase 6 skipped)

## 1) Required keys and values

Put these in `Backend/.env`:

```bash
# Nokia CAMARA auth
NOKIA_BASE_URL=https://<your-nokia-camara-base-url>
NOKIA_CLIENT_ID=<your-client-id>
NOKIA_CLIENT_SECRET=<your-client-secret>

# OR RapidAPI auth (supported directly)
RAPIDAPI_KEY=<your-rapidapi-key>
RAPIDAPI_HOST=network-as-code.nokia.rapidapi.com
RAPIDAPI_BASE_URL=https://network-as-code.p-eu.rapidapi.com

# Local API auth for TrustCall endpoint tests
TRUSTCALL_API_KEY=<any-strong-local-key>

# Optional but recommended
NOKIA_REQUEST_TIMEOUT=8
TRUSTCALL_APP_IPV4=<public-ipv4-for-qod-if-needed>
PROJECT_ID=<optional-local-if-using-secret-manager>
```

Notes:
- If you are testing locally without GCP Secret Manager, env vars are enough.
- `TRUSTCALL_APP_IPV4` is needed only for QoD session creation.
- If `RAPIDAPI_KEY` is set, TrustCall uses RapidAPI header auth instead of OAuth.

## 2) Install dependencies

```bash
cd Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Run direct Nokia smoke test (real SIM)

```bash
python scripts/test_real_sim.py --phone "+<E164_NUMBER>"
```

Optional location verification in same run:

```bash
python scripts/test_real_sim.py --phone "+<E164_NUMBER>" --latitude <lat> --longitude <lng>
```

## 4) Run TrustCall API locally

```bash
uvicorn main:app --reload --port 8000
```

Test handshake:

```bash
curl -X POST "http://127.0.0.1:8000/v1/trust-handshake" \
  -H "Content-Type: application/json" \
  -H "x-api-key: <TRUSTCALL_API_KEY>" \
  -d '{
    "phone_number": "+<E164_NUMBER>",
    "use_case": "generic",
    "requested_layers": ["identity", "integrity", "context", "quality", "ai"]
  }'
```

## 5) Common reasons real-SIM tests fail

- SIM/operator is not eligible for a specific CAMARA API product.
- Number is not in a supported market/operator for that endpoint.
- Nokia app/product is enabled but missing entitlement for a specific API.
- OAuth creds are valid but base URL points to wrong environment.
- QoD fails because `TRUSTCALL_APP_IPV4` is missing or not routable.

## 6) Minimum you need right now

- Either `NOKIA_BASE_URL` + OAuth creds, **or** `RAPIDAPI_KEY` + `RAPIDAPI_HOST` + `RAPIDAPI_BASE_URL`
- one real E.164 phone number with active SIM
- `TRUSTCALL_API_KEY` for local endpoint tests
