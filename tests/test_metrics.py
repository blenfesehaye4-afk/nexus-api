import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/metrics")
        assert res.status_code == 200
        assert "text/plain" in res.headers["content-type"]
        body = res.text
        assert "nexus_uptime_seconds" in body
        assert "nexus_http_requests_total" in body
        assert "nexus_tasks_total" in body
        assert "nexus_webhooks_total" in body
