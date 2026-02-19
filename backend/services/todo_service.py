import logging
from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, or_

from models import Todo, TodoCreate, TodoUpdate, Priority
from services.event_publisher import event_publisher
from services.recurring_task_service import create_next_occurrence

logger = logging.getLogger(__name__)


class TodoService:
    """Service class for Todo CRUD operations with event publishing."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.publisher = event_publisher

    async def get_all_todos(self) -> Sequence[Todo]:
        """Retrieve all todos ordered by creation date (newest first)."""
        statement = select(Todo).order_by(Todo.created_at.desc())
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_user_todos(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        overdue: Optional[bool] = None,
    ) -> Sequence[Todo]:
        """Retrieve todos for a specific user with optional filtering, search, and sorting."""
        statement = select(Todo).where(Todo.user_id == user_id)

        # Filter by completion status
        if status == "pending":
            statement = statement.where(Todo.completed == False)
        elif status == "completed":
            statement = statement.where(Todo.completed == True)

        # Filter by priority
        if priority:
            statement = statement.where(Todo.priority == priority)

        # Filter by tag (JSON array contains)
        if tag:
            # For both PostgreSQL (JSON) and SQLite, use string contains as fallback
            statement = statement.where(Todo.tags.isnot(None))

        # Filter overdue tasks
        if overdue:
            statement = statement.where(
                Todo.due_date.isnot(None),
                Todo.due_date < datetime.utcnow(),
                Todo.completed == False,
            )

        # Search by title/description
        if search:
            search_term = f"%{search}%"
            statement = statement.where(
                or_(
                    Todo.title.ilike(search_term),
                    Todo.description.ilike(search_term),
                )
            )

        # Sorting
        if sort_by == "priority":
            statement = statement.order_by(Todo.priority.desc().nullslast(), Todo.created_at.desc())
        elif sort_by == "due_date":
            statement = statement.order_by(Todo.due_date.asc().nullslast(), Todo.created_at.desc())
        else:
            statement = statement.order_by(Todo.created_at.desc())

        result = await self.session.execute(statement)
        todos = list(result.scalars().all())

        # Post-filter by tag (JSON array membership — compatible with both PG and SQLite)
        if tag:
            todos = [t for t in todos if t.tags and tag.lower() in [tg.lower() for tg in t.tags]]

        return todos

    async def get_todo(self, todo_id: UUID) -> Optional[Todo]:
        """Retrieve a single todo by ID."""
        statement = select(Todo).where(Todo.id == todo_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create_todo(self, data: TodoCreate) -> Todo:
        """Create a new todo and emit todo.created event."""
        todo = Todo(
            title=data.title,
            description=data.description,
            user_id=data.user_id,
            priority=data.priority,
            tags=data.tags,
            due_date=data.due_date,
            remind_at=data.remind_at,
            recurrence_rule=data.recurrence_rule,
        )
        self.session.add(todo)
        await self.session.commit()
        await self.session.refresh(todo)

        # Emit todo.created event
        try:
            self.publisher.publish_todo_created(
                todo_id=todo.id,
                title=todo.title,
                description=todo.description,
                completed=todo.completed,
                created_at=todo.created_at,
            )
        except Exception as e:
            logger.warning(f"Failed to publish todo.created event: {e}")

        return todo

    async def update_todo(self, todo_id: UUID, data: TodoUpdate) -> Optional[Todo]:
        """Update an existing todo and emit todo.updated event."""
        todo = await self.get_todo(todo_id)
        if not todo:
            return None

        # Track changes for event
        changes = {}
        previous = {}

        update_fields = ["title", "description", "priority", "tags", "due_date", "remind_at", "recurrence_rule"]
        for field_name in update_fields:
            new_val = getattr(data, field_name, None)
            if new_val is not None:
                # Treat empty string as None (clearing the field)
                if isinstance(new_val, str) and new_val.strip() == "":
                    new_val = None
                old_val = getattr(todo, field_name)
                if new_val != old_val:
                    previous[field_name] = str(old_val) if old_val is not None else None
                    changes[field_name] = str(new_val) if new_val is not None and not isinstance(new_val, (str, list)) else new_val
                    setattr(todo, field_name, new_val)

        # Only update and emit event if there are actual changes
        if changes:
            todo.updated_at = datetime.utcnow()
            self.session.add(todo)
            await self.session.commit()
            await self.session.refresh(todo)

            # Emit todo.updated event
            try:
                self.publisher.publish_todo_updated(
                    todo_id=todo.id,
                    changes=changes,
                    previous=previous,
                    updated_at=todo.updated_at,
                )
            except Exception as e:
                logger.warning(f"Failed to publish todo.updated event: {e}")

        return todo

    async def delete_todo(self, todo_id: UUID) -> bool:
        """Delete a todo by ID and emit todo.deleted event. Returns True if deleted, False if not found."""
        todo = await self.get_todo(todo_id)
        if not todo:
            return False

        # Capture title before deletion for event
        todo_title = todo.title

        await self.session.delete(todo)
        await self.session.commit()

        # Emit todo.deleted event
        try:
            self.publisher.publish_todo_deleted(
                todo_id=todo_id,
                title=todo_title,
                deleted_at=datetime.utcnow(),
            )
        except Exception as e:
            logger.warning(f"Failed to publish todo.deleted event: {e}")

        return True

    async def toggle_todo(self, todo_id: UUID) -> Optional[Todo]:
        """Toggle the completion status of a todo and emit todo.completed event."""
        todo = await self.get_todo(todo_id)
        if not todo:
            return None

        todo.completed = not todo.completed
        completed_at = datetime.utcnow() if todo.completed else None

        self.session.add(todo)
        await self.session.commit()
        await self.session.refresh(todo)

        # Emit todo.completed event
        try:
            self.publisher.publish_todo_completed(
                todo_id=todo.id,
                completed=todo.completed,
                completed_at=completed_at,
            )
        except Exception as e:
            logger.warning(f"Failed to publish todo.completed event: {e}")

        # Handle recurring tasks: create next occurrence when completed
        if todo.completed and todo.recurrence_rule:
            try:
                next_todo = await create_next_occurrence(self.session, todo)
                if next_todo:
                    logger.info(f"Created next recurring task {next_todo.id} from {todo.id}")
            except Exception as e:
                logger.warning(f"Failed to create next recurring occurrence: {e}")

        return todo

    async def get_overdue_todos(self, user_id: UUID) -> Sequence[Todo]:
        """Get all overdue, incomplete todos for a user."""
        return await self.get_user_todos(user_id, overdue=True)
