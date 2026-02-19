"""Internal API endpoints for MCP server (no auth, localhost only).

These endpoints are called by the MCP server subprocess running within
the same container. They bypass Clerk auth since the MCP server cannot
obtain JWT tokens.
"""

from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from database import get_session
from models import Todo, TodoCreate, TodoUpdate, TodoRead
from models.user import User
from services.todo_service import TodoService

router = APIRouter(prefix="/internal/todos", tags=["Internal"])


def get_todo_service(session: AsyncSession = Depends(get_session)) -> TodoService:
    return TodoService(session)


async def ensure_user_exists(user_id: UUID, session: AsyncSession) -> None:
    """Ensure a user record exists for the given UUID, create if missing."""
    result = await session.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        user = User(
            id=user_id,
            email=f"{user_id}@internal.local",
            is_active=True,
            hashed_password="internal",
        )
        session.add(user)
        await session.commit()


@router.get("", response_model=List[TodoRead])
async def list_todos(
    user_id: UUID,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    overdue: Optional[bool] = None,
    service: TodoService = Depends(get_todo_service),
):
    """List todos for a user with optional filters (internal, no auth)."""
    return await service.get_user_todos(
        user_id,
        status=status,
        priority=priority,
        tag=tag,
        search=search,
        sort_by=sort_by,
        overdue=overdue,
    )


@router.post("", response_model=TodoRead, status_code=201)
async def create_todo(
    data: TodoCreate,
    session: AsyncSession = Depends(get_session),
    service: TodoService = Depends(get_todo_service),
):
    """Create a todo (internal, no auth)."""
    if data.user_id:
        await ensure_user_exists(data.user_id, session)
    return await service.create_todo(data)


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service),
):
    """Get a single todo (internal, no auth)."""
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.put("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: UUID,
    data: TodoUpdate,
    service: TodoService = Depends(get_todo_service),
):
    """Update a todo (internal, no auth)."""
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return await service.update_todo(todo_id, data)


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service),
):
    """Delete a todo (internal, no auth)."""
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    await service.delete_todo(todo_id)
    return None


@router.patch("/{todo_id}/toggle", response_model=TodoRead)
async def toggle_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service),
):
    """Toggle todo completion (internal, no auth)."""
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return await service.toggle_todo(todo_id)
