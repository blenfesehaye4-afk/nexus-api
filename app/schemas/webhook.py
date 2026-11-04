"""Webhook schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class WebhookEndpointCreate(BaseModel):
    target_url: str = Field(..., description="Target subscriber URL")
    description: Optional[str] = "External endpoint for event streaming"
    events: List[str] = Field(default_factory=lambda: ["task.completed", "task.failed"])
    secret: Optional[str] = Field(None, description="Optional custom signing secret. Auto-generated if omitted.")


class WebhookEndpointResponse(BaseModel):
    id: str
    target_url: str
    description: Optional[str]
    events: List[str]
    secret: str
    is_active: bool
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookTriggerRequest(BaseModel):
    event_type: str = Field(..., description="Name of the event")
    payload: Dict[str, Any] = Field(default_factory=dict)


class WebhookDeliveryResponse(BaseModel):
    delivery_id: str
    endpoint_id: str
    target_url: str
    event_type: str
    status_code: Optional[int]
    signature: str
    success: bool
    response_body: Optional[str]
    delivered_at: datetime
