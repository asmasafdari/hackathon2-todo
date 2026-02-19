"""Reminder scheduler using Dapr Jobs API.

Schedules exact-time reminders via Dapr Jobs API instead of cron polling.
When a job fires, Dapr calls the /api/jobs/trigger endpoint at the
exact scheduled time.
"""

import logging
import os
from datetime import datetime
from typing import Optional
from uuid import UUID

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = int(os.environ.get("DAPR_HTTP_PORT", "3500"))
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"


async def schedule_reminder(
    task_id: UUID,
    user_id: str,
    remind_at: datetime,
    title: str,
) -> bool:
    """Schedule a reminder using Dapr Jobs API.

    Args:
        task_id: The task to remind about
        user_id: The user to notify
        remind_at: When to fire the reminder
        title: Task title for the notification

    Returns:
        True if scheduled successfully
    """
    job_name = f"reminder-task-{task_id}"
    due_time = remind_at.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DAPR_BASE_URL}/v1.0-alpha1/jobs/{job_name}",
                json={
                    "dueTime": due_time,
                    "data": {
                        "task_id": str(task_id),
                        "user_id": user_id,
                        "title": title,
                        "type": "reminder",
                    },
                },
                timeout=5.0,
            )

            if response.status_code in (200, 204):
                logger.info(f"Scheduled reminder for task {task_id} at {due_time}")
                return True
            else:
                logger.warning(
                    f"Failed to schedule reminder: {response.status_code} {response.text}"
                )
                return False

    except Exception as e:
        logger.warning(f"Dapr Jobs API not available, skipping reminder schedule: {e}")
        return False


async def cancel_reminder(task_id: UUID) -> bool:
    """Cancel a scheduled reminder.

    Args:
        task_id: The task whose reminder to cancel

    Returns:
        True if cancelled successfully
    """
    job_name = f"reminder-task-{task_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{DAPR_BASE_URL}/v1.0-alpha1/jobs/{job_name}",
                timeout=5.0,
            )

            if response.status_code in (200, 204):
                logger.info(f"Cancelled reminder for task {task_id}")
                return True
            else:
                logger.debug(f"Reminder cancellation returned {response.status_code}")
                return False

    except Exception as e:
        logger.debug(f"Dapr Jobs API not available for cancellation: {e}")
        return False
