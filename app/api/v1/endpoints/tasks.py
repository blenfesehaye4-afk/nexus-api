"""Task management and dispatch endpoints."""

import asyncio
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
from app.models.store import data_store
from app.schemas.task import TaskCreate, TaskResponse, TaskStatus
from app.schemas.user import UserResponse
from app.services.task_service import task_worker

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def dispatch_task(
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
):
    """Enqueue and trigger an asynchronous background task."""
    task = await data_store.create_task(user_id=current_user.id, task_in=task_in)
    background_tasks.add_task(task_worker.execute_task, task.id)
    return task


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    """List tasks owned by the authenticated user with optional status filter."""
    return await data_store.list_tasks(user_id=current_user.id, status=status_filter, limit=limit)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve details, live progress, and execution output for a specific task."""
    task = await data_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    return task


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(
    task_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """Cancel an active or pending task."""
    task = await data_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this task")
    if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
        raise HTTPException(status_code=400, detail=f"Cannot cancel task in '{task.status.value}' state")

    cancelled = await data_store.update_task_progress(
        task_id=task_id,
        status=TaskStatus.CANCELLED,
        progress=task.progress,
        error="Cancelled by user request.",
    )
    return cancelled
