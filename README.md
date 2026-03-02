# TrustCall

TrustCall is a telecom-native caller identity verification protocol that restores trust in voice communication.

It verifies caller identity in real time using carrier-level signals such as SIM integrity, device consistency, and number authenticity, and generates a Trust Score before the recipient answers the call.

TrustCall acts as an identity layer for telecommunications, similar to how HTTPS secures the internet.

---

# Overview

Phone calls are no longer trusted due to scam calls, SIM swap fraud, and AI voice impersonation.

TrustCall solves this by verifying caller identity at the network level and presenting a real-time Trust Score to the recipient.

This enables users, enterprises, and telecom operators to distinguish legitimate calls from high-risk ones instantly.

---

# Architecture

TrustCall is built using a layered architecture:

Interface Layer
FastAPI backend exposes verification endpoints.

Intelligence Layer
Trust Engine evaluates telecom identity signals and computes Trust Scores.

Data Layer
PostgreSQL stores call events and audit logs. Redis provides caching for low-latency verification.

Network Layer
Telecom APIs such as Nokia Network as Code provide carrier-level identity data.

---

# Repository Structure

```
trustcall/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── routes/
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── index.html
│   └── package.json
│
├── docs/
├── infra/
└── README.md
```

---

# Technology Stack

Backend
FastAPI (Python)
SQLAlchemy
PostgreSQL
Redis

Frontend
React (Vite)

Infrastructure
Docker
Telecom APIs (Nokia Network as Code compatible)

---

# How It Works

Step 1: Call is initiated
Step 2: Telecom network sends verification request to TrustCall API
Step 3: Trust Engine queries telecom identity signals
Step 4: Trust Score is computed
Step 5: Result is returned and displayed to recipient

Verification completes in milliseconds.

---

# API Endpoint

POST /verify

Request:

```
{
  "caller": "+34600123456",
  "recipient": "+34600987654"
}
```

Response:

```
{
  "trust_score": 91,
  "status": "VERIFIED"
}
```

---

# Running the Backend

Navigate to backend folder:

```
cd backend
```

Create virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```
pip install fastapi uvicorn
```

Run server:

```
uvicorn app.main:app --reload
```

API will be available at:

```
http://127.0.0.1:8000
```

Interactive API docs:

```
http://127.0.0.1:8000/docs
```

---

# Running the Frontend

Navigate to frontend folder:

```
cd frontend
npm install
npm run dev
```

Frontend will run at:

```
http://localhost:5173
```

---

# Core Components

Trust Engine
Calculates Trust Score based on telecom identity signals.

Telecom Integration Layer
Fetches carrier identity data.

Database
Stores call verification history.

Cache Layer
Improves performance and reduces latency.

API Layer
Exposes verification endpoints.

---

# Use Cases

Banks and fintech for fraud prevention
Telecom operators for verified caller services
Enterprises for trusted outbound communication
Government and emergency services

---

# Vision

TrustCall establishes a universal identity layer for voice communication.

It enables secure, verified, and trusted voice interactions at global telecom scale.

---

# Status

Prototype stage
Backend functional
Frontend functional
Telecom integration simulated

---

# Future Work

Integrate real telecom APIs
Deploy using Docker and cloud infrastructure
Add authentication and enterprise access control
Implement advanced trust scoring models
Scale for production telecom workloads

---

# License

Prototype project. All rights reserved.

