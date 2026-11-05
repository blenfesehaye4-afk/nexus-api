# 🌐 Nexus API

[![CI](https://github.com/blenfesehaye4-afk/nexus-api/actions/workflows/ci.yml/badge.svg)](https://github.com/blenfesehaye4-afk/nexus-api/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **High-performance asynchronous task orchestration, machine-to-machine API keys & HMAC-signed webhook microservice built with FastAPI.**

Nexus API is a modular backend service providing non-blocking task offloading, scoped API key authentication, telemetry instrumentation, and cryptographically verified webhook delivery with automated exponential retry schedules.

---

## 🌟 What's New in v0.2.0

- 🔑 **Machine-to-Machine Scoped API Keys**: Provision secret tokens (`nx_live_...`) with scoped authorization (`tasks:read`, `tasks:write`, `admin`) and SHA-256 hashed storage.
- 📊 **Prometheus & OpenMetrics Telemetry**: Dedicated `/api/v1/metrics` endpoint exposing real-time HTTP traffic, task lifecycle counters, and system uptime.
- 🛡️ **Dual-Mode Authentication**: Seamless support for both OAuth2 JWT Bearer tokens and `X-API-Key` headers across all protected endpoints.

---

## 🏗️ Architecture

```
[ Client / SPA / Worker ]
        │
        ├── Bearer JWT or X-API-Key
        ▼
┌───────────────────────────────────────────┐
│              Nexus API Core               │
│                                           │
│  ┌──────────────┐      ┌───────────────┐  │
│  │ Auth & Keys  │      │ Async Tasks   │  │
│  └──────┬───────┘      └───────┬───────┘  │
│         │                      │          │
│         ▼                      ▼          │
│  ┌──────────────┐      ┌───────────────┐  │
│  │  Prometheus  │      │ HMAC Webhook  │  │
│  │   Metrics    │      │  Dispatcher   │  │
│  └──────────────┘      └───────┬───────┘  │
└────────────────────────────────┼──────────┘
                                 │
                 HMAC-SHA256 Signature Header
                                 ▼
                     [ External Webhook Sink ]
```

---

## 🚀 Key Features

- ⚡ **Asynchronous Background Processing**: Offloads heavy tasks with real-time status and progress updates (`pending`, `running`, `completed`, `failed`).
- 🔐 **Dual Auth**: JWT Bearer auth for end-users + Scoped API Keys for machine-to-machine microservices.
- 🔏 **HMAC-SHA256 Signed Webhooks**: Every webhook payload includes an `X-Nexus-Signature: sha256=...` header computed using the subscriber's private secret.
- 📈 **Prometheus Observability**: Native metrics scraping support for Grafana/Prometheus monitors.
- 🐳 **Docker-Ready**: Packaged with Dockerfile and Docker Compose for instant cloud deployment.

---

## 📦 Installation & Setup

### Local Setup
```bash
git clone https://github.com/blenfesehaye4-afk/nexus-api.git
cd nexus-api
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Docker
```bash
docker compose up -d
```

Explore interactive Swagger UI at: `http://localhost:8000/docs`

---

## 🔑 Machine-to-Machine API Keys

Create a scoped key:
```bash
curl -X POST http://localhost:8000/api/v1/keys/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "ci-deployer", "scopes": ["tasks:read", "tasks:write"]}'
```

Use the key directly with `X-API-Key`:
```bash
curl http://localhost:8000/api/v1/tasks/ \
  -H "X-API-Key: nx_live_abc123..."
```

---

## 📊 Prometheus Telemetry

Scrape telemetry metrics:
```bash
curl http://localhost:8000/api/v1/metrics
```

Output sample:
```prometheus
# HELP nexus_uptime_seconds Total runtime of the Nexus API service in seconds
# TYPE nexus_uptime_seconds gauge
nexus_uptime_seconds 412.35

# HELP nexus_tasks_total Total tasks registered in system
# TYPE nexus_tasks_total gauge
nexus_tasks_total 42
```

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
