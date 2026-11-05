"""API Key generation and management endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.store import data_store
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreatedResponse, ApiKeyInfo
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_in: ApiKeyCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    """Generate a new machine-to-machine API key with specified scopes."""
    return await data_store.create_api_key(current_user.id, key_in)


@router.get("/", response_model=List[ApiKeyInfo])
async def list_api_keys(
    current_user: UserResponse = Depends(get_current_user),
):
    """List all API keys belonging to the authenticated user."""
    return await data_store.list_api_keys(current_user.id)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """Revoke an active API key."""
    success = await data_store.revoke_api_key(current_user.id, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found or does not belong to user",
        )
