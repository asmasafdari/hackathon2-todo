"""Tests for the Todo Service business logic."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Todo, TodoCreate
from backend.services.todo_service import TodoService


class TestTodoService:
    """Tests for TodoService class."""

    async def test_create_todo(self, test_session: AsyncSession):
        """Test creating a todo through service layer."""
        service = TodoService(test_session)

        todo = await service.create_todo(
            TodoCreate(title="Service Test", description="Service Description")
        )

        assert todo.title == "Service Test"
        assert todo.description == "Service Description"
        assert todo.completed is False
        assert todo.id is not None

    async def test_get_all_todos_empty(self, test_session: AsyncSession):
        """Test getting all todos when none exist."""
        service = TodoService(test_session)

        todos = await service.get_all_todos()

        assert todos == []

    async def test_get_all_todos(self, test_session: AsyncSession):
        """Test getting all todos."""
        service = TodoService(test_session)

        # Create todos
        await service.create_todo(TodoCreate(title="First"))
        await service.create_todo(TodoCreate(title="Second"))

        todos = await service.get_all_todos()

        assert len(todos) == 2
        assert todos[0].title == "First"
        assert todos[1].title == "Second"

    async def test_get_todo_by_id(self, test_session: AsyncSession):
        """Test getting a todo by ID."""
        service = TodoService(test_session)
        created = await service.create_todo(TodoCreate(title="Test"))

        todo = await service.get_todo_by_id(str(created.id))

        assert todo is not None
        assert todo.id == created.id
        assert todo.title == "Test"

    async def test_get_todo_by_id_not_found(self, test_session: AsyncSession):
        """Test getting non-existent todo returns None."""
        service = TodoService(test_session)

        todo = await service.get_todo_by_id("123e4567-e89b-12d3-a456-426614174000")

        assert todo is None

    async def test_update_todo(self, test_session: AsyncSession):
        """Test updating a todo."""
        service = TodoService(test_session)
        created = await service.create_todo(TodoCreate(title="Original"))

        updated = await service.update_todo(
            created.id, TodoUpdate(title="Updated", description="New Desc")
        )

        assert updated is not None
        assert updated.title == "Updated"
        assert updated.description == "New Desc"

    async def test_update_todo_not_found(self, test_session: AsyncSession):
        """Test updating non-existent todo returns None."""
        service = TodoService(test_session)

        from uuid import UUID

        updated = await service.update_todo(
            UUID("123e4567-e89b-12d3-a456-426614174000"), TodoUpdate(title="Updated")
        )

        assert updated is None

    async def test_toggle_todo(self, test_session: AsyncSession):
        """Test toggling a todo."""
        service = TodoService(test_session)
        created = await service.create_todo(TodoCreate(title="Toggle Test"))
        assert created.completed is False

        toggled = await service.toggle_todo(created.id)

        assert toggled is not None
        assert toggled.completed is True

    async def test_toggle_todo_not_found(self, test_session: AsyncSession):
        """Test toggling non-existent todo returns None."""
        service = TodoService(test_session)

        from uuid import UUID

        toggled = await service.toggle_todo(
            UUID("123e4567-e89b-12d3-a456-426614174000")
        )

        assert toggled is None

    async def test_delete_todo(self, test_session: AsyncSession):
        """Test deleting a todo."""
        service = TodoService(test_session)
        created = await service.create_todo(TodoCreate(title="To Delete"))

        success = await service.delete_todo(created.id)

        assert success is True

        # Verify it's deleted
        todo = await service.get_todo_by_id(created.id)
        assert todo is None

    async def test_delete_todo_not_found(self, test_session: AsyncSession):
        """Test deleting non-existent todo returns False."""
        service = TodoService(test_session)

        from uuid import UUID

        success = await service.delete_todo(
            UUID("123e4567-e89b-12d3-a456-426614174000")
        )

        assert success is False
