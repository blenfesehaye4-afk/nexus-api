"""Shared pytest fixtures."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.store import data_store


@pytest.fixture(autouse=True)
def clean_data_store():
    """Reset data store between tests."""
    data_store.users.clear()
    data_store.users_by_email.clear()
    data_store.tasks.clear()
    data_store.webhooks.clear()


@pytest.fixture
async def client():
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client: AsyncClient):
    """Register and log in a test user, returning auth Bearer headers."""
    # Register
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "developer@example.com", "password": "securepassword123", "full_name": "Test Dev"},
    )
    assert reg_resp.status_code == 201

    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "developer@example.com", "password": "securepassword123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
