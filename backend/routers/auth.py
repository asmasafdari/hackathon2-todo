"""Auth router for Clerk-authenticated user operations."""

from fastapi import APIRouter, Depends
from models import UserRead
from models.user import User
from dependencies.auth import get_current_user_id, get_or_create_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(get_or_create_user)):
    """Get the currently authenticated user's profile."""
    return user


@router.get("/verify")
async def verify_token(clerk_user_id: str = Depends(get_current_user_id)):
    """Verify the Clerk token is valid. Returns the Clerk user ID."""
    return {"authenticated": True, "clerk_user_id": clerk_user_id}
