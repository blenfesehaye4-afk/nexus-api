"""Webhook registration and simulation endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.store import data_store
from app.schemas.user import UserResponse
from app.schemas.webhook import (
    WebhookDeliveryResponse,
    WebhookEndpointCreate,
    WebhookEndpointResponse,
    WebhookTriggerRequest,
)
from app.services.webhook_service import webhook_dispatcher

router = APIRouter()


@router.post("/endpoints", response_model=WebhookEndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_endpoint(
    hook_in: WebhookEndpointCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    """Register a new external webhook subscriber URL."""
    return await data_store.create_webhook(user_id=current_user.id, hook_in=hook_in)


@router.get("/endpoints", response_model=List[WebhookEndpointResponse])
async def list_endpoints(
    current_user: UserResponse = Depends(get_current_user),
):
    """List all registered webhook endpoints for current user."""
    return await data_store.list_webhooks(user_id=current_user.id)


@router.post("/test-trigger", response_model=List[WebhookDeliveryResponse])
async def trigger_test_event(
    req: WebhookTriggerRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """Manually dispatch a test event to verify HMAC signature and delivery."""
    deliveries = await webhook_dispatcher.broadcast_event(
        event_type=req.event_type,
        payload=req.payload,
    )
    return deliveries
