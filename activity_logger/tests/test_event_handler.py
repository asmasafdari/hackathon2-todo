"""Tests for Activity Logger event handler."""

import pytest
import json
from datetime import datetime
from unittest.mock import AsyncMock

from activity_logger.handlers.event_handler import EventHandler
from activity_logger.models import ActivityLog, ProcessedEvent


class TestEventHandler:
    """Tests for EventHandler class."""

    async def test_is_already_processed_false(self, test_session):
        """Test checking unprocessed event."""
        handler = EventHandler(test_session)

        result = await handler.is_already_processed("new-event-id")

        assert result is False

    async def test_is_already_processed_true(self, test_session):
        """Test checking already processed event."""
        handler = EventHandler(test_session)

        # Add processed event
        processed = ProcessedEvent(
            event_id="processed-event-id", event_type="todo.created"
        )
        test_session.add(processed)
        await test_session.commit()

        result = await handler.is_already_processed("processed-event-id")

        assert result is True

    async def test_process_event_success(self, test_session):
        """Test processing an event."""
        handler = EventHandler(test_session)

        result = await handler.process_event(
            event_id="test-event-123",
            event_type="todo.created",
            source="/backend/todos",
            timestamp="2026-01-22T10:00:00Z",
            data={"id": "todo-123", "title": "Test Todo"},
            spec_version="1.0",
            data_content_type="application/json",
        )

        assert result is not None
        assert result.event_id == "test-event-123"
        assert result.event_type == "todo.created"
        assert result.source == "/backend/todos"
        assert result.todo_id == "todo-123"
        assert json.loads(result.data)["title"] == "Test Todo"

    async def test_process_event_idempotent(self, test_session):
        """Test that processing same event twice is idempotent."""
        handler = EventHandler(test_session)

        # Process first time
        await handler.process_event(
            event_id="duplicate-event",
            event_type="todo.created",
            source="/backend/todos",
            timestamp="2026-01-22T10:00:00Z",
            data={"id": "todo-123"},
        )

        # Process second time (should skip)
        result = await handler.process_event(
            event_id="duplicate-event",
            event_type="todo.created",
            source="/backend/todos",
            timestamp="2026-01-22T10:00:00Z",
            data={"id": "todo-123"},
        )

        assert result is None

    async def test_process_event_invalid_timestamp(self, test_session):
        """Test processing event with invalid timestamp."""
        handler = EventHandler(test_session)

        result = await handler.process_event(
            event_id="test-event",
            event_type="todo.created",
            source="/backend/todos",
            timestamp="invalid-timestamp",
            data={"id": "todo-123"},
        )

        assert result is not None
        # Should use current time as fallback
        assert result.timestamp is not None

    async def test_process_event_no_todo_id(self, test_session):
        """Test processing event without todo_id in data."""
        handler = EventHandler(test_session)

        result = await handler.process_event(
            event_id="test-event",
            event_type="agent.action.executed",
            source="/agent/mcp",
            timestamp="2026-01-22T10:00:00Z",
            data={"action": "create_todo", "success": True},
        )

        assert result is not None
        assert result.todo_id is None
        assert result.event_type == "agent.action.executed"
