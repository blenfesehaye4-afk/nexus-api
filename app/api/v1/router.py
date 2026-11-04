"""Main router aggregating all v1 endpoints."""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, health, tasks, webhooks

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
