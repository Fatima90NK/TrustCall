#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:8000}"
API_KEY="${TRUSTCALL_API_KEY:-local-dev-trustcall-key}"
PHONE="${TEST_PHONE_E164:-+99999991000}"

curl -sS -X POST "${API_URL}/v1/trust-handshake" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d "{\"phone_number\": \"${PHONE}\", \"use_case\": \"generic\", \"requested_layers\": [\"identity\", \"integrity\", \"context\", \"quality\", \"ai\"]}" \
  | python -m json.tool
