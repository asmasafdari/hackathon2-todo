"""
Event publisher service using Dapr pub/sub.

This module provides a unified interface for publishing CloudEvents
to Kafka topics via Dapr's pub/sub building block.
"""

import json
import logging
import os
import socket
from datetime import datetime
from typing import Optional
from uuid import UUID

from dapr.clients import DaprClient

from events.types import (
    PUBSUB_NAME,
    SOURCE_BACKEND,
    EVENT_TODO_CREATED,
    EVENT_TODO_UPDATED,
    EVENT_TODO_COMPLETED,
    EVENT_TODO_DELETED,
    EVENT_REMINDER_DUE,
    EVENT_RECURRING_CREATED,
    TOPIC_TODO_CREATED,
    TOPIC_TODO_UPDATED,
    TOPIC_TODO_COMPLETED,
    TOPIC_TODO_DELETED,
    TOPIC_TASK_EVENTS,
    TOPIC_REMINDERS,
    TOPIC_TASK_UPDATES,
)
from events.schemas import (
    CloudEventEnvelope,
    TodoCreatedData,
    TodoUpdatedData,
    TodoCompletedData,
    TodoDeletedData,
    ReminderDueData,
    RecurringTaskCreatedData,
)

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = int(os.environ.get("DAPR_HTTP_PORT", "3500"))


def _check_dapr_available() -> bool:
    """Quick 1-second socket check to see if the Dapr sidecar is reachable."""
    try:
        with socket.create_connection(("127.0.0.1", DAPR_HTTP_PORT), timeout=1):
            return True
    except (ConnectionRefusedError, OSError, socket.timeout):
        return False


class EventPublisher:
    """
    Publishes domain events to Kafka via Dapr pub/sub.

    All events are wrapped in CloudEvents envelope and validated
    before publishing. No direct Kafka client usage.
    """

    def __init__(self, pubsub_name: str = PUBSUB_NAME):
        self.pubsub_name = pubsub_name
        self._dapr_available: Optional[bool] = None

    def _is_dapr_available(self) -> bool:
        """Check if Dapr sidecar is available, caching the result on success."""
        if self._dapr_available is True:
            return True
        available = _check_dapr_available()
        self._dapr_available = available if available else None
        return available

    def _publish_event(self, topic: str, event: CloudEventEnvelope) -> bool:
        """
        Internal method to publish a CloudEvent to a topic.

        Validates the event against CloudEvents schema before publishing.
        Returns True if published successfully, False otherwise.
        """
        if not self._is_dapr_available():
            logger.warning(
                f"Dapr sidecar not available on port {DAPR_HTTP_PORT}, "
                f"skipping event {event.id} to {topic}"
            )
            return False

        try:
            # Validate the event envelope
            event.model_validate(event.model_dump())
            logger.debug(f"Event {event.id} validated successfully")

            event_dict = event.to_dict()
            logger.info(
                f"Publishing event {event.id} to topic {topic}: type={event.type}"
            )

            with DaprClient() as client:
                client.publish_event(
                    pubsub_name=self.pubsub_name,
                    topic_name=topic,
                    data=json.dumps(event_dict),
                    data_content_type="application/cloudevents+json",
                )

            logger.info(f"Successfully published event {event.id} to {topic}")
            return True

        except Exception as e:
            self._dapr_available = None
            logger.error(f"Failed to publish event {event.id} to {topic}: {e}")
            return False

    def _publish_to_aggregate(self, topic: str, event: CloudEventEnvelope) -> None:
        """Also publish to aggregate topics for Phase V consumers."""
        try:
            self._publish_event(topic, event)
        except Exception as e:
            logger.debug(f"Failed to publish to aggregate topic {topic}: {e}")

    def publish_todo_created(
        self,
        todo_id: UUID,
        title: str,
        description: Optional[str],
        completed: bool,
        created_at: datetime,
        actor_id: Optional[str] = None,
    ) -> bool:
        """Publish a todo.created event."""
        data = TodoCreatedData(
            id=todo_id,
            title=title,
            description=description,
            completed=completed,
            created_at=created_at,
            actor_id=actor_id,
        )

        event = CloudEventEnvelope(
            source=SOURCE_BACKEND,
            type=EVENT_TODO_CREATED,
            subject=str(todo_id),
            data=data.model_dump(mode="json"),
        )

        result = self._publish_event(TOPIC_TODO_CREATED, event)
        # Also publish to aggregate topics
        self._publish_to_aggregate(TOPIC_TASK_EVENTS, event)
        self._publish_to_aggregate(TOPIC_TASK_UPDATES, event)
        return result

    def publish_todo_updated(
        self,
        todo_id: UUID,
        changes: dict,
        previous: dict,
        updated_at: datetime,
        actor_id: Optional[str] = None,
    ) -> bool:
        """Publish a todo.updated event."""
        data = TodoUpdatedData(
            id=todo_id,
            changes=changes,
            previous=previous,
            updated_at=updated_at,
            actor_id=actor_id,
        )

        event = CloudEventEnvelope(
            source=SOURCE_BACKEND,
            type=EVENT_TODO_UPDATED,
            subject=str(todo_id),
            data=data.model_dump(mode="json"),
        )

        result = self._publish_event(TOPIC_TODO_UPDATED, event)
        self._publish_to_aggregate(TOPIC_TASK_EVENTS, event)
        self._publish_to_aggregate(TOPIC_TASK_UPDATES, event)
        return result

    def publish_todo_completed(
        self,
        todo_id: UUID,
        completed: bool,
        completed_at: Optional[datetime],
        actor_id: Optional[str] = None,
    ) -> bool:
        """Publish a todo.completed event."""
        data = TodoCompletedData(
            id=todo_id,
            completed=completed,
            completed_at=completed_at,
            actor_id=actor_id,
        )

        event = CloudEventEnvelope(
            source=SOURCE_BACKEND,
            type=EVENT_TODO_COMPLETED,
            subject=str(todo_id),
            data=data.model_dump(mode="json"),
        )

        result = self._publish_event(TOPIC_TODO_COMPLETED, event)
        self._publish_to_aggregate(TOPIC_TASK_EVENTS, event)
        self._publish_to_aggregate(TOPIC_TASK_UPDATES, event)
        return result

    def publish_todo_deleted(
        self,
        todo_id: UUID,
        title: str,
        deleted_at: datetime,
        actor_id: Optional[str] = None,
    ) -> bool:
        """Publish a todo.deleted event."""
        data = TodoDeletedData(
            id=todo_id,
            title=title,
            deleted_at=deleted_at,
            actor_id=actor_id,
        )

        event = CloudEventEnvelope(
            source=SOURCE_BACKEND,
            type=EVENT_TODO_DELETED,
            subject=str(todo_id),
            data=data.model_dump(mode="json"),
        )

        result = self._publish_event(TOPIC_TODO_DELETED, event)
        self._publish_to_aggregate(TOPIC_TASK_EVENTS, event)
        self._publish_to_aggregate(TOPIC_TASK_UPDATES, event)
        return result

    def publish_reminder_due(
        self,
        task_id: UUID,
        title: str,
        due_at: Optional[datetime],
        remind_at: datetime,
        user_id: str,
    ) -> bool:
        """Publish a reminder.due event to the reminders topic."""
        data = ReminderDueData(
            task_id=task_id,
            title=title,
            due_at=due_at,
            remind_at=remind_at,
            user_id=user_id,
        )

        event = CloudEventEnvelope(
            source=SOURCE_BACKEND,
            type=EVENT_REMINDER_DUE,
            subject=str(task_id),
            data=data.model_dump(mode="json"),
        )

        return self._publish_event(TOPIC_REMINDERS, event)

    def publish_recurring_created(
        self,
        new_id: UUID,
        parent_id: UUID,
        title: str,
        recurrence_rule: str,
        due_date: Optional[datetime],
    ) -> bool:
        """Publish a todo.recurring.created event."""
        data = RecurringTaskCreatedData(
            id=new_id,
            parent_id=parent_id,
            title=title,
            recurrence_rule=recurrence_rule,
            due_date=due_date,
        )

        event = CloudEventEnvelope(
            source=SOURCE_BACKEND,
            type=EVENT_RECURRING_CREATED,
            subject=str(new_id),
            data=data.model_dump(mode="json"),
        )

        result = self._publish_event(TOPIC_TASK_EVENTS, event)
        self._publish_to_aggregate(TOPIC_TASK_UPDATES, event)
        return result


# Singleton instance for use across the application
event_publisher = EventPublisher()
