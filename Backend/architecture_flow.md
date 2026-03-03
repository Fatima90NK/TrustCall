# TrustCall Backend Flow (Layer + API Composition)

This document explains how the `POST /v1/trust-handshake` pipeline works, which Nokia APIs feed each layer, and how the final trust score is composed.

## 1) End-to-End Request Flow

```mermaid
flowchart TD
    A[Mobile/Web Client] -->|POST /v1/trust-handshake| B[FastAPI Route]
    B --> C[Auth Middleware x-api-key]
    C --> D[TrustCallEngine.run]

    D --> E1[Identity Layer]
    D --> E2[Integrity Layer]
    D --> E3[Context Layer]
    D --> E4[Quality Layer]

    E1 --> F[Merge Layer Results]
    E2 --> F
    E3 --> F
    E4 --> F

    F --> G[AI Layer Rule Engine]
    G --> H[Score + Badge + TTL]
    H --> I[Save to Firestore]
    H --> J[TrustCallResponse]
```

Notes:
- Layers run in parallel via async orchestration.
- Partial API failures are handled gracefully (layer returns result with error field instead of crashing request).
- Firestore persists handshake results for retrieval by request ID.

## 2) Layer → API Mapping

```mermaid
flowchart LR
    subgraph Identity
      I1[Number Verification]
      I2[KYC Fill-in]
      I3[KYC Match]
    end

    subgraph Integrity
      R1[SIM Swap]
      R2[Device Swap]
      R3[Number Recycling]
      R4[Call Forwarding Signal]
    end

    subgraph Context
      C1[Location Retrieval]
      C2[Location Verification optional]
      C3[KYC Tenure]
    end

    subgraph Quality
      Q1[Device Status Connectivity]
      Q2[QoD Session optional]
    end

    subgraph AI
      A1[Rule Engine from merged signals]
    end
```

### Current RapidAPI endpoint set in use

- Number Verification
  - `POST /passthrough/camara/v1/number-verification/number-verification/v0/verify`
  - Requires consent auth (`Bearer token` or `code/state`)
- SIM Swap
  - `POST /passthrough/camara/v1/sim-swap/sim-swap/v0/check`
- Device Swap
  - `POST /passthrough/camara/v1/device-swap/device-swap/v1/check`
- Number Recycling
  - `POST /passthrough/camara/v1/number-recycling/number-recycling/v0.2/check`
- Call Forwarding Signal
  - `POST /passthrough/camara/v1/call-forwarding-signal/call-forwarding-signal/v0.3/unconditional-call-forwardings`
- Device Status
  - `POST /device-status/v0/connectivity`
- Location Retrieval
  - `POST /location-retrieval/v0/retrieve`
- KYC Tenure
  - `POST /passthrough/camara/v1/kyc-tenure/kyc-tenure/v0.1/check-tenure`

## 3) Scoring Composition

```mermaid
flowchart TD
    S0[BASE_SCORE = 50] --> S1[Apply Identity delta * weight]
    S1 --> S2[Apply Integrity delta * weight]
    S2 --> S3[Apply Context delta * weight]
    S3 --> S4[Apply Quality delta * weight]
    S4 --> S5[Apply AI delta * weight]
    S5 --> S6[Clamp 0..100]
    S6 --> S7[Badge Assignment]

    S7 --> T1[TRUSTED >= 70]
    S7 --> T2[CAUTION 40..69]
    S7 --> T3[UNTRUSTED < 40]
```

Use-case weights are applied per layer (`generic`, `banking`, `enterprise`, `emergency`).

## 4) Layer Delta Logic (high-level)

- Identity:
  - positive if number verified / strong KYC match
  - neutralized to `0` when Number Verification or KYC match is unavailable
- Integrity:
  - heavy negative penalties for risk flags (`sim_swapped`, `device_swapped`, `number_recycled`, `call_forwarding_active`)
- Context:
  - positive for validated location / strong tenure
  - tenure contribution neutralized when tenure API is unavailable/mismatch
- Quality:
  - small positive for `CONNECTED_DATA`, negative for `NOT_CONNECTED`
- AI:
  - rule-based confidence adjustment from aggregate red/green flags

## 5) Response Shape (what is composed)

Final response includes:
- `badge`
- `composite_score`
- `layer_results` (each with `score_delta`, `signals`, `apis_called`, `latency_ms`, `error`)
- `confidence`
- `ttl_seconds`

This is the full trust composition output returned to client apps.
