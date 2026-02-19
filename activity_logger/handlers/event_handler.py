"""Idempotent event handler for processing CloudEvents."""

import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from activity_logger.models import ActivityLog, ProcessedEvent

logger = logging.getLogger(__name__)


class EventHandler:
    """Handles CloudEvents with idempotent processing."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_already_processed(self, event_id: str) -> bool:
        """Check if event was already processed (idempotency)."""
        result = await self.session.execute(
            select(ProcessedEvent).where(ProcessedEvent.event_id == event_id)
        )
        return result.scalar_one_or_none() is not None

    async def process_event(
        self,
        event_id: str,
        event_type: str,
        source: str,
        timestamp: str,
        data: dict[str, Any],
        spec_version: str = "1.0",
        data_content_type: str = "application/json",
    ) -> ActivityLog | None:
        """
        Process a CloudEvent idempotently.

        Args:
            event_id: Unique event ID from CloudEvent
            event_type: Event type (e.g., todo.created)
            source: Event source (e.g., /backend/todos)
            timestamp: Event timestamp (ISO format)
            data: Event payload
            spec_version: CloudEvents spec version
            data_content_type: Content type of data

        Returns:
            ActivityLog entry if processed, None if already processed
        """
        # Check idempotency
        if await self.is_already_processed(event_id):
            logger.debug(f"Event {event_id} already processed, skipping")
            return None

        # Parse timestamp
        try:
            event_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            event_timestamp = datetime.utcnow()

        # Extract todo_id from data if present
        todo_id = data.get("id") if isinstance(data, dict) else None

        # Create activity log entry
        activity_log = ActivityLog(
            event_id=event_id,
            event_type=event_type,
            source=source,
            timestamp=event_timestamp,
            spec_version=spec_version,
            data_content_type=data_content_type,
            data=json.dumps(data),
            todo_id=str(todo_id) if todo_id else None,
        )

        self.session.add(activity_log)

        # Mark event as processed for idempotency
        processed_event = ProcessedEvent(event_id=event_id, event_type=event_type)
        self.session.add(processed_event)

        await self.session.commit()

        logger.info(f"Processed event {event_id} of type {event_type}")
        return activity_log
