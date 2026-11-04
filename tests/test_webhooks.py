"""Test suite for webhook management and signature validation."""

import pytest
from httpx import AsyncClient
from app.core.security import compute_hmac_signature


@pytest.mark.asyncio
async def test_webhook_crud(client: AsyncClient, auth_headers: dict):
    # 1. Register Webhook
    hook_payload = {
        "target_url": "https://example.com/webhook",
        "description": "Payment and task notifier",
        "events": ["task.completed"],
    }
    create_resp = await client.post("/api/v1/webhooks/endpoints", json=hook_payload, headers=auth_headers)
    assert create_resp.status_code == 201
    created_hook = create_resp.json()
    assert created_hook["target_url"] == "https://example.com/webhook"
    assert created_hook["secret"].startswith("whsec_")

    # 2. List Webhooks
    list_resp = await client.get("/api/v1/webhooks/endpoints", headers=auth_headers)
    assert list_resp.status_code == 200
    hooks = list_resp.json()
    assert len(hooks) == 1


@pytest.mark.asyncio
async def test_hmac_signature_calculation():
    secret = "test-secret-key-123"
    payload = b'{"event":"task.completed","status":"ok"}'
    sig = compute_hmac_signature(secret, payload)
    assert len(sig) == 64  # SHA256 hex string
    # Verify deterministic signature
    assert sig == compute_hmac_signature(secret, payload)
