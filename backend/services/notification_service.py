"""Notification service consumer.

Consumes from the 'reminders' Dapr pub/sub topic and logs/sends
notifications when reminders are due.

In Kubernetes, this runs as a separate deployment with Dapr sidecar.
Dapr delivers messages via HTTP POST to the subscription endpoint.
"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


async def handle_reminder_event(event_data: dict) -> dict:
    """Process a reminder event from the reminders topic.

    Args:
        event_data: CloudEvents payload with reminder data

    Returns:
        Status dict
    """
    data = event_data.get("data", {})
    task_id = data.get("task_id")
    title = data.get("title", "Unknown task")
    user_id = data.get("user_id", "unknown")
    remind_at = data.get("remind_at")

    logger.info(
        f"[NOTIFICATION] Reminder due for user={user_id}: "
        f"task={task_id} title='{title}' remind_at={remind_at}"
    )

    # TODO: In production, send push notification / email / WebSocket message
    # For now, log the reminder as processed
    return {
        "status": "processed",
        "task_id": task_id,
        "user_id": user_id,
        "processed_at": datetime.utcnow().isoformat(),
    }
