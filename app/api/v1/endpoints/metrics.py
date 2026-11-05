"""Prometheus & system telemetry metrics endpoint."""

from fastapi import APIRouter, Response
from app.models.store import data_store

router = APIRouter()


@router.get("", response_class=Response)
async def get_metrics():
    """Returns system telemetry in Prometheus text exposition format."""
    stats = data_store.get_metrics_snapshot()
    lines = [
        "# HELP nexus_uptime_seconds Total runtime of the Nexus API service in seconds",
        "# TYPE nexus_uptime_seconds gauge",
        f"nexus_uptime_seconds {stats['uptime_seconds']}",
        "",
        "# HELP nexus_http_requests_total Total HTTP requests handled",
        "# TYPE nexus_http_requests_total counter",
        f"nexus_http_requests_total {stats['requests_total']}",
        "",
        "# HELP nexus_tasks_total Total tasks registered in system",
        "# TYPE nexus_tasks_total gauge",
        f"nexus_tasks_total {stats['tasks_total']}",
        "",
        "# HELP nexus_users_total Total registered users",
        "# TYPE nexus_users_total gauge",
        f"nexus_users_total {stats['users_total']}",
        "",
        "# HELP nexus_webhooks_total Total webhook endpoints configured",
        "# TYPE nexus_webhooks_total gauge",
        f"nexus_webhooks_total {stats['webhooks_total']}",
        "",
        "# HELP nexus_active_api_keys Total active API keys",
        "# TYPE nexus_active_api_keys gauge",
        f"nexus_active_api_keys {stats['active_api_keys']}",
        "",
    ]
    return Response(content="\n".join(lines), media_type="text/plain; version=0.0.4")
