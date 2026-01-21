from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import Todo, TodoCreate, TodoUpdate, TodoRead
from services.todo_service import TodoService

router = APIRouter(prefix="/api/todos", tags=["Todos"])


def get_todo_service(session: AsyncSession = Depends(get_session)) -> TodoService:
    """Dependency to get TodoService instance."""
    return TodoService(session)


@router.get("", response_model=List[TodoRead])
async def list_todos(service: TodoService = Depends(get_todo_service)):
    """Retrieve all todos ordered by creation date (newest first)."""
    return await service.get_all_todos()


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service)
):
    """Retrieve a single todo by ID."""
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.post("", response_model=TodoRead, status_code=201)
async def create_todo(
    data: TodoCreate,
    service: TodoService = Depends(get_todo_service)
):
    """Create a new todo."""
    return await service.create_todo(data)


@router.put("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: UUID,
    data: TodoUpdate,
    service: TodoService = Depends(get_todo_service)
):
    """Update an existing todo."""
    todo = await service.update_todo(todo_id, data)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service)
):
    """Delete a todo by ID."""
    deleted = await service.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")
    return None


@router.patch("/{todo_id}/toggle", response_model=TodoRead)
async def toggle_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service)
):
    """Toggle the completion status of a todo."""
    todo = await service.toggle_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
