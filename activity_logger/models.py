"""Database models for Activity Logger service."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ActivityLog(SQLModel, table=True):
    """Activity log entry for audit trail."""

    __tablename__ = "activity_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_id: str = Field(index=True, description="CloudEvent ID")
    event_type: str = Field(index=True, description="Event type (e.g., todo.created)")
    source: str = Field(description="Event source (e.g., /backend/todos)")
    timestamp: datetime = Field(index=True, description="Event timestamp")
    spec_version: str = Field(default="1.0", description="CloudEvents spec version")
    data_content_type: Optional[str] = Field(
        default="application/json", description="Content type"
    )
    data: str = Field(description="Event payload as JSON string")
    todo_id: Optional[str] = Field(
        default=None, index=True, description="Related todo ID if applicable"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="When log entry was created"
    )


class ProcessedEvent(SQLModel, table=True):
    """Tracks processed events for idempotency."""

    __tablename__ = "processed_events"

    event_id: str = Field(primary_key=True, description="CloudEvent ID")
    processed_at: datetime = Field(
        default_factory=datetime.utcnow, description="When event was processed"
    )
    event_type: str = Field(description="Type of event processed")


class ActivityLogRead(SQLModel):
    """Schema for reading activity log entries."""

    id: UUID
    event_id: str
    event_type: str
    source: str
    timestamp: datetime
    spec_version: str
    data_content_type: Optional[str]
    data: str
    todo_id: Optional[str]
    created_at: datetime


class ActivityStats(SQLModel):
    """Statistics for activity logs."""

    total_events: int
    events_by_type: dict[str, int]
    date_range: dict[str, datetime]
