"""Test suite for task dispatching and lifecycle."""

import asyncio
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dispatch_and_query_task(client: AsyncClient, auth_headers: dict):
    # Dispatch task
    task_payload = {
        "title": "Batch Email Report",
        "task_type": "email_digest",
        "payload": {"recipient_count": 42},
        "priority": "high",
    }
    create_resp = await client.post("/api/v1/tasks/", json=task_payload, headers=auth_headers)
    assert create_resp.status_code == 202
    task = create_resp.json()
    task_id = task["id"]
    assert task["title"] == "Batch Email Report"
    assert task["priority"] == "high"

    # Wait briefly for background execution simulation
    await asyncio.sleep(0.15)

    # Check updated task
    get_resp = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    updated_task = get_resp.json()
    assert updated_task["status"] == "completed"
    assert updated_task["progress"] == 100
    assert updated_task["result"] is not None


@pytest.mark.asyncio
async def test_list_tasks_filter(client: AsyncClient, auth_headers: dict):
    # Create 2 tasks
    await client.post("/api/v1/tasks/", json={"title": "Task 1", "task_type": "job"}, headers=auth_headers)
    await client.post("/api/v1/tasks/", json={"title": "Task 2", "task_type": "job"}, headers=auth_headers)

    resp = await client.get("/api/v1/tasks/", headers=auth_headers)
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 2


@pytest.mark.asyncio
async def test_cancel_task(client: AsyncClient, auth_headers: dict):
    # Create task without immediate worker execution
    from app.models.store import data_store
    user_me = (await client.get("/api/v1/auth/me", headers=auth_headers)).json()
    from app.schemas.task import TaskCreate
    task = await data_store.create_task(user_id=user_me["id"], task_in=TaskCreate(title="Long Task", task_type="heavy"))

    cancel_resp = await client.post(f"/api/v1/tasks/{task.id}/cancel", headers=auth_headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"
