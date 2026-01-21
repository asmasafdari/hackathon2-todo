from uuid import UUID
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import Todo, TodoCreate, TodoUpdate


class TodoService:
    """Service class for Todo CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_todos(self) -> Sequence[Todo]:
        """Retrieve all todos ordered by creation date (newest first)."""
        statement = select(Todo).order_by(Todo.created_at.desc())
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_todo(self, todo_id: UUID) -> Optional[Todo]:
        """Retrieve a single todo by ID."""
        statement = select(Todo).where(Todo.id == todo_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create_todo(self, data: TodoCreate) -> Todo:
        """Create a new todo."""
        todo = Todo(
            title=data.title,
            description=data.description
        )
        self.session.add(todo)
        await self.session.commit()
        await self.session.refresh(todo)
        return todo

    async def update_todo(self, todo_id: UUID, data: TodoUpdate) -> Optional[Todo]:
        """Update an existing todo."""
        todo = await self.get_todo(todo_id)
        if not todo:
            return None

        if data.title is not None:
            todo.title = data.title
        if data.description is not None:
            todo.description = data.description

        self.session.add(todo)
        await self.session.commit()
        await self.session.refresh(todo)
        return todo

    async def delete_todo(self, todo_id: UUID) -> bool:
        """Delete a todo by ID. Returns True if deleted, False if not found."""
        todo = await self.get_todo(todo_id)
        if not todo:
            return False

        await self.session.delete(todo)
        await self.session.commit()
        return True

    async def toggle_todo(self, todo_id: UUID) -> Optional[Todo]:
        """Toggle the completion status of a todo."""
        todo = await self.get_todo(todo_id)
        if not todo:
            return None

        todo.completed = not todo.completed
        self.session.add(todo)
        await self.session.commit()
        await self.session.refresh(todo)
        return todo
