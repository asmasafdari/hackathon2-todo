"""Event publisher for the Agent MCP server."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Optional

from cloudevents.http import CloudEvent, to_json

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes events to Dapr pub/sub."""

    def __init__(self):
        self.dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.pubsub_name = "kafka-pubsub"

    def _create_cloud_event(
        self,
        event_type: str,
        source: str,
        data: dict[str, Any],
        event_id: Optional[str] = None,
    ) -> CloudEvent:
        """Create a CloudEvent with the given attributes."""
        return CloudEvent(
            {
                "specversion": "1.0",
                "type": event_type,
                "source": source,
                "id": event_id or f"{datetime.utcnow().isoformat()}-{event_type}",
                "time": datetime.utcnow().isoformat(),
                "datacontenttype": "application/json",
            },
            data,
        )

    async def publish_event(
        self,
        topic: str,
        event_type: str,
        data: dict[str, Any],
        source: str = "/agent/mcp",
        event_id: Optional[str] = None,
    ) -> bool:
        """
        Publish an event to Kafka via Dapr.

        Args:
            topic: Kafka topic name (e.g., 'agent-action-executed')
            event_type: CloudEvent type (e.g., 'com.desktoptodo.agent.action.executed')
            data: Event payload
            source: Event source
            event_id: Optional event ID

        Returns:
            True if published successfully, False otherwise
        """
        try:
            import httpx

            # Create CloudEvent
            event = self._create_cloud_event(event_type, source, data, event_id)
            event_data = to_json(event)

            # Publish via Dapr sidecar
            dapr_url = f"http://localhost:{self.dapr_port}/v1.0/publish/{self.pubsub_name}/{topic}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    dapr_url,
                    content=event_data,
                    headers={"Content-Type": "application/cloudevents+json"},
                )

                if response.status_code == 204:
                    logger.info(f"Published event to {topic}: {event_type}")
                    return True
                else:
                    logger.error(
                        f"Failed to publish event: {response.status_code} - {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False

    async def publish_agent_action_executed(
        self,
        tool: str,
        params: dict[str, Any],
        result: dict[str, Any],
        duration_ms: Optional[float] = None,
    ) -> bool:
        """Publish an agent.action.executed event."""
        return await self.publish_event(
            topic="agent-action-executed",
            event_type="com.desktoptodo.agent.action.executed",
            data={
                "tool": tool,
                "params": params,
                "result": result,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def publish_agent_action_failed(
        self,
        tool: str,
        params: dict[str, Any],
        error: str,
        error_type: str,
        duration_ms: Optional[float] = None,
    ) -> bool:
        """Publish an agent.action.failed event."""
        return await self.publish_event(
            topic="agent-action-failed",
            event_type="com.desktoptodo.agent.action.failed",
            data={
                "tool": tool,
                "params": params,
                "error": error,
                "error_type": error_type,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


# Singleton instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get or create the event publisher singleton."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
