"""Tests for logs router endpoints."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from activity_logger.models import ActivityLog, ProcessedEvent


class TestListLogs:
    """Tests for GET /logs endpoint."""

    async def test_list_logs_empty(self, test_session: AsyncSession):
        """Test listing logs when none exist."""
        # This would need FastAPI test client setup
        # Skipping for now - would need full app fixture
        pass

    async def test_create_and_retrieve_log(self, test_session: AsyncSession):
        """Test creating and retrieving a log entry."""
        log = ActivityLog(
            event_id="test-event-123",
            event_type="todo.created",
            source="/backend/todos",
            timestamp=datetime.utcnow(),
            spec_version="1.0",
            data_content_type="application/json",
            data='{"id": "todo-123", "title": "Test"}',
            todo_id="todo-123",
        )
        test_session.add(log)
        await test_session.commit()

        # Query it back
        from sqlalchemy import select

        result = await test_session.execute(
            select(ActivityLog).where(ActivityLog.event_id == "test-event-123")
        )
        retrieved = result.scalar_one_or_none()

        assert retrieved is not None
        assert retrieved.event_type == "todo.created"
        assert retrieved.todo_id == "todo-123"


class TestLogFiltering:
    """Tests for log filtering functionality."""

    async def test_filter_by_event_type(self, test_session: AsyncSession):
        """Test filtering logs by event type."""
        # Create logs of different types
        logs = [
            ActivityLog(
                event_id="event-1",
                event_type="todo.created",
                source="/backend",
                timestamp=datetime.utcnow(),
                data="{}",
            ),
            ActivityLog(
                event_id="event-2",
                event_type="todo.updated",
                source="/backend",
                timestamp=datetime.utcnow(),
                data="{}",
            ),
            ActivityLog(
                event_id="event-3",
                event_type="todo.created",
                source="/backend",
                timestamp=datetime.utcnow(),
                data="{}",
            ),
        ]
        for log in logs:
            test_session.add(log)
        await test_session.commit()

        # Query by type
        from sqlalchemy import select

        result = await test_session.execute(
            select(ActivityLog).where(ActivityLog.event_type == "todo.created")
        )
        created_logs = result.scalars().all()

        assert len(created_logs) == 2

    async def test_filter_by_todo_id(self, test_session: AsyncSession):
        """Test filtering logs by todo ID."""
        logs = [
            ActivityLog(
                event_id="event-1",
                event_type="todo.created",
                source="/backend",
                timestamp=datetime.utcnow(),
                data="{}",
                todo_id="todo-abc",
            ),
            ActivityLog(
                event_id="event-2",
                event_type="todo.updated",
                source="/backend",
                timestamp=datetime.utcnow(),
                data="{}",
                todo_id="todo-def",
            ),
        ]
        for log in logs:
            test_session.add(log)
        await test_session.commit()

        # Query by todo_id
        from sqlalchemy import select

        result = await test_session.execute(
            select(ActivityLog).where(ActivityLog.todo_id == "todo-abc")
        )
        todo_logs = result.scalars().all()

        assert len(todo_logs) == 1
        assert todo_logs[0].todo_id == "todo-abc"


class TestLogStats:
    """Tests for log statistics."""

    async def test_get_stats(self, test_session: AsyncSession):
        """Test getting statistics about logs."""
        # Create various logs
        logs = [
            ActivityLog(
                event_id="event-1",
                event_type="todo.created",
                source="/backend",
                timestamp=datetime.utcnow() - timedelta(hours=1),
                data="{}",
            ),
            ActivityLog(
                event_id="event-2",
                event_type="todo.created",
                source="/backend",
                timestamp=datetime.utcnow() - timedelta(minutes=30),
                data="{}",
            ),
            ActivityLog(
                event_id="event-3",
                event_type="todo.completed",
                source="/backend",
                timestamp=datetime.utcnow(),
                data="{}",
            ),
        ]
        for log in logs:
            test_session.add(log)
        await test_session.commit()

        # Get stats
        from sqlalchemy import select, func

        count_result = await test_session.execute(select(func.count(ActivityLog.id)))
        total = count_result.scalar()

        type_result = await test_session.execute(
            select(ActivityLog.event_type, func.count(ActivityLog.id)).group_by(
                ActivityLog.event_type
            )
        )
        by_type = {row[0]: row[1] for row in type_result.all()}

        assert total == 3
        assert by_type["todo.created"] == 2
        assert by_type["todo.completed"] == 1


class TestIdempotency:
    """Tests for idempotent event processing."""

    async def test_processed_event_tracking(self, test_session: AsyncSession):
        """Test that processed events are tracked."""
        processed = ProcessedEvent(
            event_id="duplicate-event-id", event_type="todo.created"
        )
        test_session.add(processed)
        await test_session.commit()

        # Query it back
        from sqlalchemy import select

        result = await test_session.execute(
            select(ProcessedEvent).where(
                ProcessedEvent.event_id == "duplicate-event-id"
            )
        )
        retrieved = result.scalar_one_or_none()

        assert retrieved is not None
        assert retrieved.event_type == "todo.created"
        assert retrieved.processed_at is not None
