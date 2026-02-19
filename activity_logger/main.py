"""FastAPI app with Dapr pub/sub subscriptions."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from activity_logger.database import get_session, init_db
from activity_logger.handlers.event_handler import EventHandler
from activity_logger.routers import logs

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    logger.info("Activity Logger service started")
    yield


app = FastAPI(
    title="Activity Logger Service",
    description="Event consumer and audit trail API for Todo Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(logs.router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "activity-logger",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Dapr pub/sub event handlers
# These endpoints are called by Dapr sidecar when events are published


@app.post("/events/todo-created")
async def handle_todo_created(
    event_data: dict[str, Any], session: AsyncSession = Depends(get_session)
):
    """Handle todo.created events from Dapr pub/sub."""
    handler = EventHandler(session)

    # Extract CloudEvent fields
    event_id = event_data.get("id", "")
    event_type = event_data.get("type", "")
    source = event_data.get("source", "")
    timestamp = event_data.get("time", "")
    data = event_data.get("data", {})
    spec_version = event_data.get("specversion", "1.0")
    data_content_type = event_data.get("datacontenttype", "application/json")

    await handler.process_event(
        event_id=event_id,
        event_type=event_type,
        source=source,
        timestamp=timestamp,
        data=data,
        spec_version=spec_version,
        data_content_type=data_content_type,
    )

    return {"status": "ok"}


@app.post("/events/todo-updated")
async def handle_todo_updated(
    event_data: dict[str, Any], session: AsyncSession = Depends(get_session)
):
    """Handle todo.updated events from Dapr pub/sub."""
    handler = EventHandler(session)

    await handler.process_event(
        event_id=event_data.get("id", ""),
        event_type=event_data.get("type", ""),
        source=event_data.get("source", ""),
        timestamp=event_data.get("time", ""),
        data=event_data.get("data", {}),
        spec_version=event_data.get("specversion", "1.0"),
        data_content_type=event_data.get("datacontenttype", "application/json"),
    )

    return {"status": "ok"}


@app.post("/events/todo-completed")
async def handle_todo_completed(
    event_data: dict[str, Any], session: AsyncSession = Depends(get_session)
):
    """Handle todo.completed events from Dapr pub/sub."""
    handler = EventHandler(session)

    await handler.process_event(
        event_id=event_data.get("id", ""),
        event_type=event_data.get("type", ""),
        source=event_data.get("source", ""),
        timestamp=event_data.get("time", ""),
        data=event_data.get("data", {}),
        spec_version=event_data.get("specversion", "1.0"),
        data_content_type=event_data.get("datacontenttype", "application/json"),
    )

    return {"status": "ok"}


@app.post("/events/todo-deleted")
async def handle_todo_deleted(
    event_data: dict[str, Any], session: AsyncSession = Depends(get_session)
):
    """Handle todo.deleted events from Dapr pub/sub."""
    handler = EventHandler(session)

    await handler.process_event(
        event_id=event_data.get("id", ""),
        event_type=event_data.get("type", ""),
        source=event_data.get("source", ""),
        timestamp=event_data.get("time", ""),
        data=event_data.get("data", {}),
        spec_version=event_data.get("specversion", "1.0"),
        data_content_type=event_data.get("datacontenttype", "application/json"),
    )

    return {"status": "ok"}


@app.post("/events/agent-action-executed")
async def handle_agent_action_executed(
    event_data: dict[str, Any], session: AsyncSession = Depends(get_session)
):
    """Handle agent.action.executed events from Dapr pub/sub."""
    handler = EventHandler(session)

    await handler.process_event(
        event_id=event_data.get("id", ""),
        event_type=event_data.get("type", ""),
        source=event_data.get("source", ""),
        timestamp=event_data.get("time", ""),
        data=event_data.get("data", {}),
        spec_version=event_data.get("specversion", "1.0"),
        data_content_type=event_data.get("datacontenttype", "application/json"),
    )

    return {"status": "ok"}


@app.post("/events/agent-action-failed")
async def handle_agent_action_failed(
    event_data: dict[str, Any], session: AsyncSession = Depends(get_session)
):
    """Handle agent.action.failed events from Dapr pub/sub."""
    handler = EventHandler(session)

    await handler.process_event(
        event_id=event_data.get("id", ""),
        event_type=event_data.get("type", ""),
        source=event_data.get("source", ""),
        timestamp=event_data.get("time", ""),
        data=event_data.get("data", {}),
        spec_version=event_data.get("specversion", "1.0"),
        data_content_type=event_data.get("datacontenttype", "application/json"),
    )

    return {"status": "ok"}


@app.post("/events/reminder-due")
async def handle_reminder_due(
    event_data: dict[str, Any], session: AsyncSession = Depends(get_session)
):
    """Handle reminder.due events from Dapr pub/sub."""
    handler = EventHandler(session)

    await handler.process_event(
        event_id=event_data.get("id", ""),
        event_type=event_data.get("type", "com.desktoptodo.reminder.due"),
        source=event_data.get("source", ""),
        timestamp=event_data.get("time", ""),
        data=event_data.get("data", {}),
        spec_version=event_data.get("specversion", "1.0"),
        data_content_type=event_data.get("datacontenttype", "application/json"),
    )

    return {"status": "ok"}


@app.post("/events/recurring-created")
async def handle_recurring_created(
    event_data: dict[str, Any], session: AsyncSession = Depends(get_session)
):
    """Handle todo.recurring.created events from Dapr pub/sub."""
    handler = EventHandler(session)

    await handler.process_event(
        event_id=event_data.get("id", ""),
        event_type=event_data.get("type", "com.desktoptodo.todo.recurring.created"),
        source=event_data.get("source", ""),
        timestamp=event_data.get("time", ""),
        data=event_data.get("data", {}),
        spec_version=event_data.get("specversion", "1.0"),
        data_content_type=event_data.get("datacontenttype", "application/json"),
    )

    return {"status": "ok"}
