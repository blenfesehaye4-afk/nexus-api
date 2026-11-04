"""Test suite for authentication workflows."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_user_registration_and_login(client: AsyncClient):
    # 1. Register
    reg_data = {"email": "alice@nexus.io", "password": "supersecretpassword", "full_name": "Alice Nexus"}
    reg_resp = await client.post("/api/v1/auth/register", json=reg_data)
    assert reg_resp.status_code == 201
    user_info = reg_resp.json()
    assert user_info["email"] == "alice@nexus.io"
    assert "id" in user_info

    # 2. Duplicate registration fails
    dup_resp = await client.post("/api/v1/auth/register", json=reg_data)
    assert dup_resp.status_code == 400

    # 3. Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "alice@nexus.io", "password": "supersecretpassword"},
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 4. Get Profile
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "alice@nexus.io"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "bob@nexus.io", "password": "correctpassword123"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "bob@nexus.io", "password": "wrongpassword"},
    )
    assert login_resp.status_code == 401
