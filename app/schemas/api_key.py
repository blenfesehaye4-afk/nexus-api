"""Pydantic schemas for machine-to-machine API key management."""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Descriptive identifier for the API key")
    scopes: List[str] = Field(default_factory=lambda: ["tasks:read", "tasks:write"], description="Scoped permission list")


class ApiKeyCreatedResponse(BaseModel):
    id: str
    name: str
    key: str = Field(..., description="Full API secret key, displayed only once upon generation")
    scopes: List[str]
    created_at: datetime


class ApiKeyInfo(BaseModel):
    id: str
    name: str
    key_prefix: str = Field(..., description="Truncated key prefix, e.g. 'nx_live_abcd...'")
    scopes: List[str]
    is_active: bool
    created_at: datetime
