from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import Todo, TodoCreate, TodoUpdate, TodoRead
from models.user import User
from services.todo_service import TodoService
from dependencies.auth import get_or_create_user

router = APIRouter(prefix="/api/todos", tags=["Todos"])


def get_todo_service(session: AsyncSession = Depends(get_session)) -> TodoService:
    """Dependency to get TodoService instance."""
    return TodoService(session)


@router.get("", response_model=List[TodoRead])
async def list_todos(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    overdue: Optional[bool] = None,
    current_user: User = Depends(get_or_create_user),
    service: TodoService = Depends(get_todo_service),
):
    """Retrieve todos for the authenticated user with optional filtering."""
    return await service.get_user_todos(
        current_user.id,
        status=status,
        priority=priority,
        tag=tag,
        search=search,
        sort_by=sort_by,
        overdue=overdue,
    )


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: UUID,
    current_user: User = Depends(get_or_create_user),
    service: TodoService = Depends(get_todo_service),
):
    """Retrieve a single todo by ID."""
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id and todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return todo


@router.post("", response_model=TodoRead, status_code=201)
async def create_todo(
    data: TodoCreate,
    current_user: User = Depends(get_or_create_user),
    service: TodoService = Depends(get_todo_service),
):
    """Create a new todo for the authenticated user."""
    data.user_id = current_user.id
    return await service.create_todo(data)


@router.put("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: UUID,
    data: TodoUpdate,
    current_user: User = Depends(get_or_create_user),
    service: TodoService = Depends(get_todo_service),
):
    """Update an existing todo."""
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id and todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    updated = await service.update_todo(todo_id, data)
    return updated


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: UUID,
    current_user: User = Depends(get_or_create_user),
    service: TodoService = Depends(get_todo_service),
):
    """Delete a todo by ID."""
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id and todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    await service.delete_todo(todo_id)
    return None


@router.patch("/{todo_id}/toggle", response_model=TodoRead)
async def toggle_todo(
    todo_id: UUID,
    current_user: User = Depends(get_or_create_user),
    service: TodoService = Depends(get_todo_service),
):
    """Toggle the completion status of a todo."""
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id and todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    toggled = await service.toggle_todo(todo_id)
    return toggled
