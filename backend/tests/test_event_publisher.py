"""Tests for the backend event publisher."""

import json
import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import MagicMock, patch

from backend.services.event_publisher import EventPublisher, event_publisher
from backend.events.types import (
    SOURCE_BACKEND,
    EVENT_TODO_CREATED,
    EVENT_TODO_UPDATED,
    EVENT_TODO_COMPLETED,
    EVENT_TODO_DELETED,
)


class TestEventPublisher:
    """Tests for EventPublisher class."""

    def test_init_default(self):
        """Test EventPublisher initializes with defaults."""
        publisher = EventPublisher()

        assert publisher.pubsub_name == "kafka-pubsub"

    def test_init_custom_pubsub(self):
        """Test EventPublisher with custom pubsub name."""
        publisher = EventPublisher(pubsub_name="custom-pubsub")

        assert publisher.pubsub_name == "custom-pubsub"

    @patch("backend.services.event_publisher.DaprClient")
    def test_publish_todo_created(self, mock_dapr_client):
        """Test publishing todo.created event."""
        # Setup mock
        mock_client = MagicMock()
        mock_dapr_client.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_dapr_client.return_value.__exit__ = MagicMock(return_value=False)

        publisher = EventPublisher()
        todo_id = uuid4()
        created_at = datetime.utcnow()

        result = publisher.publish_todo_created(
            todo_id=todo_id,
            title="Test Todo",
            description="Test Description",
            completed=False,
            created_at=created_at,
            actor_id="user-123",
        )

        assert result is True
        mock_client.publish_event.assert_called_once()

        # Verify the call arguments
        call_args = mock_client.publish_event.call_args
        assert call_args.kwargs["pubsub_name"] == "kafka-pubsub"
        assert call_args.kwargs["topic_name"] == "todo.created"

    @patch("backend.services.event_publisher.DaprClient")
    def test_publish_todo_updated(self, mock_dapr_client):
        """Test publishing todo.updated event."""
        # Setup mock
        mock_client = MagicMock()
        mock_dapr_client.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_dapr_client.return_value.__exit__ = MagicMock(return_value=False)

        publisher = EventPublisher()
        todo_id = uuid4()
        updated_at = datetime.utcnow()

        result = publisher.publish_todo_updated(
            todo_id=todo_id,
            changes={"title": "Updated Title"},
            previous={"title": "Old Title"},
            updated_at=updated_at,
            actor_id="user-123",
        )

        assert result is True
        mock_client.publish_event.assert_called_once()

        call_args = mock_client.publish_event.call_args
        assert call_args.kwargs["topic_name"] == "todo.updated"

    @patch("backend.services.event_publisher.DaprClient")
    def test_publish_todo_completed(self, mock_dapr_client):
        """Test publishing todo.completed event."""
        # Setup mock
        mock_client = MagicMock()
        mock_dapr_client.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_dapr_client.return_value.__exit__ = MagicMock(return_value=False)

        publisher = EventPublisher()
        todo_id = uuid4()
        completed_at = datetime.utcnow()

        result = publisher.publish_todo_completed(
            todo_id=todo_id,
            completed=True,
            completed_at=completed_at,
            actor_id="user-123",
        )

        assert result is True
        mock_client.publish_event.assert_called_once()

        call_args = mock_client.publish_event.call_args
        assert call_args.kwargs["topic_name"] == "todo.completed"

    @patch("backend.services.event_publisher.DaprClient")
    def test_publish_todo_deleted(self, mock_dapr_client):
        """Test publishing todo.deleted event."""
        # Setup mock
        mock_client = MagicMock()
        mock_dapr_client.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_dapr_client.return_value.__exit__ = MagicMock(return_value=False)

        publisher = EventPublisher()
        todo_id = uuid4()
        deleted_at = datetime.utcnow()

        result = publisher.publish_todo_deleted(
            todo_id=todo_id,
            title="Deleted Todo",
            deleted_at=deleted_at,
            actor_id="user-123",
        )

        assert result is True
        mock_client.publish_event.assert_called_once()

        call_args = mock_client.publish_event.call_args
        assert call_args.kwargs["topic_name"] == "todo.deleted"

    @patch("backend.services.event_publisher.DaprClient")
    def test_publish_event_failure(self, mock_dapr_client):
        """Test handling of publish failure."""
        # Setup mock to raise exception
        mock_dapr_client.return_value.__enter__ = MagicMock(
            side_effect=Exception("Dapr connection failed")
        )

        publisher = EventPublisher()
        todo_id = uuid4()

        result = publisher.publish_todo_created(
            todo_id=todo_id,
            title="Test",
            description=None,
            completed=False,
            created_at=datetime.utcnow(),
        )

        assert result is False


class TestEventPublisherSingleton:
    """Tests for the event_publisher singleton."""

    def test_singleton_exists(self):
        """Test that event_publisher singleton exists."""
        assert event_publisher is not None
        assert isinstance(event_publisher, EventPublisher)

    def test_singleton_default_pubsub(self):
        """Test singleton uses default pubsub name."""
        assert event_publisher.pubsub_name == "kafka-pubsub"
