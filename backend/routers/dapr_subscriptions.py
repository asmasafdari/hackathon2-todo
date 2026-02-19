"""Dapr pub/sub subscription endpoints.

These endpoints are called by the Dapr sidecar when events arrive
on subscribed topics. The /dapr/subscribe endpoint tells Dapr
which topics this app subscribes to.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request

from services.notification_service import handle_reminder_event
from services.recurring_task_consumer import handle_task_event
from routers.websocket import broadcast_task_update

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Dapr"])


@router.get("/dapr/subscribe")
async def dapr_subscribe():
    """Dapr calls this to discover pub/sub subscriptions."""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-events",
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/events/reminders",
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-updates",
            "route": "/events/task-updates",
        },
    ]


@router.post("/events/task-events")
async def handle_task_events(event_data: dict[str, Any]):
    """Handle events from the task-events topic."""
    logger.debug(f"Received task-event: {event_data.get('type', 'unknown')}")
    result = await handle_task_event(event_data)
    return {"status": "SUCCESS"}


@router.post("/events/reminders")
async def handle_reminders(event_data: dict[str, Any]):
    """Handle events from the reminders topic."""
    logger.debug(f"Received reminder event")
    result = await handle_reminder_event(event_data)
    return {"status": "SUCCESS"}


@router.post("/events/task-updates")
async def handle_task_updates(event_data: dict[str, Any]):
    """Handle events from the task-updates topic — broadcast to WebSocket clients."""
    logger.debug(f"Received task-update for WebSocket broadcast")
    await broadcast_task_update(event_data)
    return {"status": "SUCCESS"}


@router.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """Dapr Jobs API calls this endpoint when a scheduled job fires."""
    job_data = await request.json()
    data = job_data.get("data", {})
    job_type = data.get("type", "")

    if job_type == "reminder":
        logger.info(f"Reminder job fired for task {data.get('task_id')}")
        await handle_reminder_event({
            "type": "com.desktoptodo.reminder.due",
            "data": data,
        })

    return {"status": "SUCCESS"}


@router.post("/cron-reminder")
async def handle_cron_binding(request: Request):
    """
    Called by Dapr cron binding (dapr/components/oke/bindings-cron.yaml) every minute.

    Acts as a safety-net alongside the Dapr Jobs API exact-time reminders.
    Logs each tick so missed reminders surface in structured logs / Grafana.
    In production, extend this to query and re-queue any stuck reminders.
    """
    logger.info("Cron binding tick — reminder safety-net check")
    return {"status": "SUCCESS", "timestamp": datetime.utcnow().isoformat()}
