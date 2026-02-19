"""Tests for the agent event publisher."""

import json
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from agent.event_publisher import EventPublisher, get_event_publisher


class TestEventPublisher:
    """Tests for EventPublisher class."""

    def test_init_default(self):
        """Test EventPublisher initializes with defaults."""
        publisher = EventPublisher()

        assert publisher.dapr_port == "3500"
        assert publisher.pubsub_name == "kafka-pubsub"

    def test_init_custom_port(self, monkeypatch):
        """Test EventPublisher uses DAPR_HTTP_PORT env var."""
        monkeypatch.setenv("DAPR_HTTP_PORT", "5000")
        publisher = EventPublisher()

        assert publisher.dapr_port == "5000"

    def test_create_cloud_event(self):
        """Test CloudEvent creation."""
        publisher = EventPublisher()

        event = publisher._create_cloud_event(
            event_type="com.desktoptodo.agent.action.executed",
            source="/agent/mcp",
            data={"tool": "create_todo", "params": {}},
            event_id="test-event-id",
        )

        assert event["type"] == "com.desktoptodo.agent.action.executed"
        assert event["source"] == "/agent/mcp"
        assert event["id"] == "test-event-id"
        assert event["specversion"] == "1.0"
        assert event["datacontenttype"] == "application/json"
        assert "time" in event

    def test_create_cloud_event_auto_id(self):
        """Test CloudEvent creates ID if not provided."""
        publisher = EventPublisher()

        event = publisher._create_cloud_event(
            event_type="com.desktoptodo.agent.action.executed",
            source="/agent/mcp",
            data={},
        )

        assert event["id"] is not None
        assert len(event["id"]) > 0

    @pytest.mark.asyncio
    async def test_publish_event_success(self):
        """Test successful event publishing."""
        publisher = EventPublisher()

        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
            result = await publisher.publish_event(
                topic="agent-action-executed",
                event_type="com.desktoptodo.agent.action.executed",
                data={"tool": "create_todo"},
            )

            assert result is True
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_event_failure(self):
        """Test event publishing failure handling."""
        publisher = EventPublisher()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            result = await publisher.publish_event(
                topic="agent-action-executed",
                event_type="com.desktoptodo.agent.action.executed",
                data={"tool": "create_todo"},
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_publish_event_exception(self):
        """Test event publishing handles exceptions."""
        publisher = EventPublisher()

        with patch(
            "httpx.AsyncClient.post", side_effect=Exception("Connection failed")
        ):
            result = await publisher.publish_event(
                topic="agent-action-executed",
                event_type="com.desktoptodo.agent.action.executed",
                data={"tool": "create_todo"},
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_publish_agent_action_executed(self):
        """Test publishing agent.action.executed event."""
        publisher = EventPublisher()

        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
            result = await publisher.publish_agent_action_executed(
                tool="create_todo",
                params={"title": "Test"},
                result={"id": "123"},
                duration_ms=150.5,
            )

            assert result is True

            # Verify the call was made with correct parameters
            call_args = mock_post.call_args
            assert "agent-action-executed" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_publish_agent_action_failed(self):
        """Test publishing agent.action.failed event."""
        publisher = EventPublisher()

        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
            result = await publisher.publish_agent_action_failed(
                tool="create_todo",
                params={"title": "Test"},
                error="Connection refused",
                error_type="ConnectionError",
                duration_ms=50.0,
            )

            assert result is True

            # Verify the call was made with correct parameters
            call_args = mock_post.call_args
            assert "agent-action-failed" in call_args[0][0]


class TestGetEventPublisher:
    """Tests for get_event_publisher singleton."""

    def test_singleton(self):
        """Test that get_event_publisher returns singleton."""
        publisher1 = get_event_publisher()
        publisher2 = get_event_publisher()

        assert publisher1 is publisher2

    def test_singleton_same_instance(self):
        """Test singleton returns same instance across calls."""
        # Reset singleton for test
        import agent.event_publisher as ep

        ep._event_publisher = None

        publisher1 = get_event_publisher()
        publisher2 = get_event_publisher()

        assert publisher1 is publisher2
        assert isinstance(publisher1, EventPublisher)
