"""Background task orchestration and execution service."""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

from app.models.store import data_store
from app.schemas.task import TaskStatus, TaskResponse
from app.services.webhook_service import webhook_dispatcher


class TaskWorker:
    """Simulates asynchronous background worker execution with progress reporting."""

    async def execute_task(self, task_id: str) -> None:
        """Asynchronously process a queued task with status updates."""
        # Step 1: Mark Running
        await data_store.update_task_progress(task_id, TaskStatus.RUNNING, progress=10)
        await asyncio.sleep(0.05)

        # Step 2: Intermediate Progress
        await data_store.update_task_progress(task_id, TaskStatus.RUNNING, progress=60)
        await asyncio.sleep(0.05)

        # Step 3: Complete and produce result
        task = await data_store.get_task(task_id)
        if not task or task.status == TaskStatus.CANCELLED:
            return

        result = {
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
            "items_processed": len(task.payload.get("items", [1])),
            "message": f"Task '{task.title}' completed successfully.",
        }

        updated = await data_store.update_task_progress(
            task_id,
            status=TaskStatus.COMPLETED,
            progress=100,
            result=result,
        )

        # Broadcast webhook event
        if updated:
            asyncio.create_task(
                webhook_dispatcher.broadcast_event(
                    event_type="task.completed",
                    payload={"task_id": updated.id, "title": updated.title, "result": updated.result},
                )
            )


task_worker = TaskWorker()
