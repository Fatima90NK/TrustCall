# TrustCall

Telecom-native caller identity verification using network signals (SIM/device/number integrity) to compute a real-time **Trust Score** before the recipient answers.

## What’s new (backend)

The backend has been upgraded from a simple `/verify` prototype into an end-to-end **Trust Handshake** workflow integrated with **Nokia Network as Code** (via **RapidAPI**, with OAuth fallback) and persistent storage.

- Primary API: `POST /v1/trust-handshake`
- Status lookup: `GET /v1/trust-handshake/{request_id}`
- Persistence: Firestore read/write for handshake results
- Scoring: layered trust engine (identity, integrity, context, quality, ai) with weighted deltas, badge assignment, and TTL policy
- Degradation: unavailable/unauthorized signals are neutralized (delta `0`) instead of penalized

---

## Architecture (high level)

**Interface Layer**
- FastAPI exposes Trust Handshake endpoints.

**Intelligence Layer**
- Trust Engine orchestrates telecom identity signals and computes a composite score + badge.

**Data Layer**
- Firestore persists handshake requests/responses.
- (Planned/optional) Postgres + Redis are referenced in the prototype README but are not the primary persistence in the current backend handoff.

**Network Layer**
- Nokia Network as Code (CAMARA APIs) via RapidAPI; OAuth where required.

---

## Repository structure (current)

```text
TrustCall/
├── Backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── scripts/
│   └── README.md
├── Frontend/
│   ├── src/
│   ├── package.json
│   └── README.md
└── README.md
```

> Note: The folder names in this repo are `Backend/` and `Frontend/` (capitalized).

---

## Backend: run locally

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

Interactive API docs (when enabled):

```text
http://127.0.0.1:8000/docs
```

### Environment

Create `Backend/.env` (see `Backend/README.md` for the full, current list). Minimum for RapidAPI mode:

```bash
RAPIDAPI_KEY=<your-rapidapi-key>
RAPIDAPI_HOST=network-as-code.nokia.rapidapi.com
RAPIDAPI_BASE_URL=https://network-as-code.p-eu.rapidapi.com
TRUSTCALL_API_KEY=<your-local-key>
```

---

## API (current)

### Start a trust handshake

`POST /v1/trust-handshake`

Request (example):

```json
{
  "phone_e164": "+34640032379"
}
```

Response (shape varies by signal availability):
- `request_id`
- `composite_score`
- `badge`
- per-layer deltas and evidence

### Fetch handshake results

`GET /v1/trust-handshake/{request_id}`

---

## Telecom signals (CAMARA) used by the backend

Working now via RapidAPI:
- SIM Swap
- Device Swap
- Number Recycling
- Call Forwarding Signal
- Device Status (Connectivity)
- Location Retrieval

Conditionally working:
- KYC Tenure (scenario-dependent)

Requires consent flow:
- Number Verification

---

## Frontend

```bash
cd Frontend
npm install
npm run dev
```

---

## Status

Prototype / active backend iteration:
- Backend: integrated with Nokia Network as Code (RapidAPI) + Firestore persistence
- Frontend: present (Vite/React) and runnable

---

## License

Prototype project. All rights reserved.
