<div align="center">

# 🌐 nexus-api

**High-Performance Asynchronous Task Orchestration & Webhook Microservice**

[![CI](https://github.com/blenfesehaye4-afk/nexus-api/actions/workflows/ci.yml/badge.svg)](https://github.com/blenfesehaye4-afk/nexus-api/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Ready](https://img.shields.io/badge/Docker-enabled-blue.svg?logo=docker&logoColor=white)](https://www.docker.com/)

A modern, scalable FastAPI backend microservice featuring non-blocking background task scheduling, cryptographically signed webhook event broadcasting (HMAC-SHA256), and secure JWT authentication.

</div>

---

## 🏗️ Architecture Overview

```
                         ┌──────────────────────────────────────────┐
                         │               Client Request             │
                         └────────────────────┬─────────────────────┘
                                              │
                                              ▼
                         ┌──────────────────────────────────────────┐
                         │         FastAPI Router & Security        │
                         │    - OAuth2 Bearer (JWT Verification)    │
                         │    - Pydantic v2 Request Validation      │
                         └──────────────┬───────────────────┬───────┘
                                        │                   │
                        ┌───────────────▼────────┐  ┌───────▼──────────────┐
                        │   Task Orchestrator    │  │  Webhook Subsystem   │
                        │ - Async worker queue   │  │ - HMAC-SHA256 signed │
                        │ - Status & Progress    │  │ - Event broadcasting │
                        └───────────────┬────────┘  └───────┬──────────────┘
                                        │                   │
                                        ▼                   ▼
                         ┌──────────────────────────────────────────┐
                         │   External Receivers / State Store       │
                         └──────────────────────────────────────────┘
```

---

## ⚡ Key Features

- 🔐 **OAuth2 & JWT Authentication**: User registration, bcrypt password hashing, and signed JWT session management.
- ⏱️ **Asynchronous Task Queue**: Non-blocking background job scheduling with real-time progress percentages and state tracking (`pending` ➔ `running` ➔ `completed` / `cancelled`).
- 🪝 **Cryptographic Webhook Broadcasting**: External URL subscription management with `HMAC-SHA256` payload signatures transmitted in `X-Nexus-Signature` headers.
- 📖 **Interactive OpenAPI Documentation**: Built-in Swagger UI (`/docs`) and ReDoc (`/redoc`).
- 🐳 **Containerized Deployment**: Ready out-of-the-box with multi-stage `Dockerfile` and `docker-compose.yml`.
- 🧪 **Comprehensive Test Coverage**: Automated asynchronous integration tests with `pytest-asyncio` and `httpx`.

---

## 🚀 Quickstart

### 1. Local Setup

```bash
git clone https://github.com/blenfesehaye4-afk/nexus-api.git
cd nexus-api
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### 2. Run the Application

```bash
uvicorn app.main:app --reload --port 8000
```
Open **[http://localhost:8000/docs](http://localhost:8000/docs)** to explore the interactive Swagger documentation.

### 3. Run with Docker Compose

```bash
docker compose up --build
```

---

## 📡 API Reference

### Health & Auth
- `GET  /api/v1/health` - Service health status
- `POST /api/v1/auth/register` - Create user account
- `POST /api/v1/auth/login` - Authenticate and get JWT token
- `GET  /api/v1/auth/me` - Authenticated user profile

### Asynchronous Tasks
- `POST /api/v1/tasks/` - Dispatch new background task
- `GET  /api/v1/tasks/` - List tasks (filter by `?status=completed`)
- `GET  /api/v1/tasks/{id}` - Inspect task progress and outputs
- `POST /api/v1/tasks/{id}/cancel` - Cancel active task

### Webhook Delivery
- `POST /api/v1/webhooks/endpoints` - Register subscriber endpoint with signing secret
- `GET  /api/v1/webhooks/endpoints` - List subscribed endpoints
- `POST /api/v1/webhooks/test-trigger` - Dispatch test event with HMAC verification

---

## 🔒 Webhook Verification Example (Python Receiver)

```python
import hmac, hashlib

def verify_nexus_signature(payload_bytes: bytes, secret: str, received_sig: str) -> bool:
    expected_sig = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, received_sig)
```

---

## 🧪 Testing

```bash
pytest -v
```

---

## 📜 License

MIT License © 2026 Blen Fesehaye
