"""Thread-safe async in-memory persistence store."""

import asyncio
import secrets
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.schemas.task import TaskCreate, TaskPriority, TaskResponse, TaskStatus
from app.schemas.user import UserCreate, UserResponse
from app.schemas.webhook import WebhookEndpointCreate, WebhookEndpointResponse
from app.core.security import get_password_hash


class MemoryDataStore:
    """Async-safe storage repository for users, tasks, and webhook subscriptions."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self.users: Dict[str, dict] = {}             # user_id -> user dict
        self.users_by_email: Dict[str, str] = {}     # email -> user_id
        self.tasks: Dict[str, dict] = {}             # task_id -> task dict
        self.webhooks: Dict[str, dict] = {}          # webhook_id -> webhook dict

    # --- User operations ---
    async def create_user(self, user_in: UserCreate) -> UserResponse:
        async with self._lock:
            if user_in.email.lower() in self.users_by_email:
                raise ValueError("A user with this email already exists.")

            user_id = f"usr_{uuid.uuid4().hex[:12]}"
            hashed_pw = get_password_hash(user_in.password)
            now = datetime.now(timezone.utc)

            user_record = {
                "id": user_id,
                "email": user_in.email.lower(),
                "full_name": user_in.full_name,
                "hashed_password": hashed_pw,
                "is_active": user_in.is_active,
                "created_at": now,
            }
            self.users[user_id] = user_record
            self.users_by_email[user_in.email.lower()] = user_id

            return UserResponse(**user_record)

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        async with self._lock:
            user_id = self.users_by_email.get(email.lower())
            if not user_id:
                return None
            return self.users.get(user_id)

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        async with self._lock:
            record = self.users.get(user_id)
            if not record:
                return None
            return UserResponse(**record)

    # --- Task operations ---
    async def create_task(self, user_id: str, task_in: TaskCreate) -> TaskResponse:
        async with self._lock:
            task_id = f"tsk_{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc)

            task_record = {
                "id": task_id,
                "title": task_in.title,
                "task_type": task_in.task_type,
                "status": TaskStatus.PENDING,
                "priority": task_in.priority,
                "payload": task_in.payload,
                "result": None,
                "error": None,
                "progress": 0,
                "user_id": user_id,
                "created_at": now,
                "updated_at": now,
            }
            self.tasks[task_id] = task_record
            return TaskResponse(**task_record)

    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        async with self._lock:
            record = self.tasks.get(task_id)
            if not record:
                return None
            return TaskResponse(**record)

    async def list_tasks(
        self,
        user_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 50,
    ) -> List[TaskResponse]:
        async with self._lock:
            results = list(self.tasks.values())
            if user_id:
                results = [t for t in results if t["user_id"] == user_id]
            if status:
                results = [t for t in results if t["status"] == status]
            results.sort(key=lambda t: t["created_at"], reverse=True)
            return [TaskResponse(**t) for t in results[:limit]]

    async def update_task_progress(
        self,
        task_id: str,
        status: TaskStatus,
        progress: int,
        result: Optional[dict] = None,
        error: Optional[str] = None,
    ) -> Optional[TaskResponse]:
        async with self._lock:
            record = self.tasks.get(task_id)
            if not record:
                return None
            record["status"] = status
            record["progress"] = progress
            if result is not None:
                record["result"] = result
            if error is not None:
                record["error"] = error
            record["updated_at"] = datetime.now(timezone.utc)
            return TaskResponse(**record)

    # --- Webhook operations ---
    async def create_webhook(self, user_id: str, hook_in: WebhookEndpointCreate) -> WebhookEndpointResponse:
        async with self._lock:
            hook_id = f"wh_{uuid.uuid4().hex[:12]}"
            secret = hook_in.secret or f"whsec_{secrets.token_hex(24)}"
            now = datetime.now(timezone.utc)

            record = {
                "id": hook_id,
                "target_url": hook_in.target_url,
                "description": hook_in.description,
                "events": hook_in.events,
                "secret": secret,
                "is_active": True,
                "user_id": user_id,
                "created_at": now,
            }
            self.webhooks[hook_id] = record
            return WebhookEndpointResponse(**record)

    async def list_webhooks(self, user_id: Optional[str] = None) -> List[WebhookEndpointResponse]:
        async with self._lock:
            results = list(self.webhooks.values())
            if user_id:
                results = [h for h in results if h["user_id"] == user_id]
            return [WebhookEndpointResponse(**h) for h in results]

    async def get_webhooks_for_event(self, event_type: str) -> List[dict]:
        async with self._lock:
            matches = []
            for h in self.webhooks.values():
                if h["is_active"] and (event_type in h["events"] or "*" in h["events"]):
                    matches.append(h)
            return matches


# Global singleton store
data_store = MemoryDataStore()
