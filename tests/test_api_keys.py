import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_api_key_lifecycle_and_authentication():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register user
        reg_res = await ac.post("/api/v1/auth/register", json={
            "email": "keyuser@example.com",
            "password": "Password123!",
            "full_name": "API Key Tester"
        })
        assert reg_res.status_code == 201

        # Login
        login_res = await ac.post("/api/v1/auth/login", data={
            "username": "keyuser@example.com",
            "password": "Password123!"
        })
        token = login_res.json()["access_token"]
        auth_header = {"Authorization": f"Bearer {token}"}

        # Generate API key
        key_res = await ac.post(
            "/api/v1/keys/",
            json={"name": "test-ci-key", "scopes": ["tasks:read", "tasks:write"]},
            headers=auth_header,
        )
        assert key_res.status_code == 201
        key_data = key_res.json()
        assert "key" in key_data
        assert key_data["key"].startswith("nx_live_")
        api_key = key_data["key"]
        key_id = key_data["id"]

        # List keys
        list_res = await ac.get("/api/v1/keys/", headers=auth_header)
        assert list_res.status_code == 200
        keys_list = list_res.json()
        assert any(k["id"] == key_id for k in keys_list)

        # Authenticate using X-API-Key instead of Bearer token
        task_res = await ac.post(
            "/api/v1/tasks/",
            json={"title": "M2M Task", "task_type": "report_generation", "payload": {"foo": "bar"}},
            headers={"X-API-Key": api_key},
        )
        assert task_res.status_code == 202
        assert task_res.json()["title"] == "M2M Task"

        # Revoke API key
        del_res = await ac.delete(f"/api/v1/keys/{key_id}", headers=auth_header)
        assert del_res.status_code == 204

        # Using revoked key fails
        failed_res = await ac.post(
            "/api/v1/tasks/",
            json={"title": "Should Fail", "task_type": "report_generation"},
            headers={"X-API-Key": api_key},
        )
        assert failed_res.status_code == 401
