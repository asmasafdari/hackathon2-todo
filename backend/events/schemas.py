"""
CloudEvents schemas for the Todo platform.

All events conform to CloudEvents v1.0 specification.
https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

from .types import CLOUDEVENTS_SPEC_VERSION


class CloudEventEnvelope(BaseModel):
    """
    CloudEvents v1.0 envelope schema.

    Required fields: specversion, id, source, type
    Recommended fields: time, datacontenttype
    """

    specversion: str = Field(
        default=CLOUDEVENTS_SPEC_VERSION,
        description="CloudEvents specification version"
    )
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this event"
    )
    source: str = Field(
        ...,
        description="Identifies the context in which an event happened"
    )
    type: str = Field(
        ...,
        description="Event type in reverse-DNS notation"
    )
    time: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the event occurred"
    )
    datacontenttype: str = Field(
        default="application/json",
        description="Content type of the data attribute"
    )
    subject: Optional[str] = Field(
        default=None,
        description="Identifies the subject of the event (e.g., entity ID)"
    )
    data: Any = Field(
        ...,
        description="Event-specific payload"
    )

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("source must be a URI-reference starting with /")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if not v.startswith("com.desktoptodo."):
            raise ValueError("type must follow pattern com.desktoptodo.<domain>.<action>")
        return v

    def to_dict(self) -> dict:
        """Convert to dictionary for Dapr pub/sub."""
        return {
            "specversion": self.specversion,
            "id": self.id,
            "source": self.source,
            "type": self.type,
            "time": self.time.isoformat() + "Z",
            "datacontenttype": self.datacontenttype,
            "subject": self.subject,
            "data": self.data if isinstance(self.data, dict) else self.data.model_dump() if hasattr(self.data, 'model_dump') else self.data,
        }


# --------------------
# Todo Domain Events
# --------------------

class TodoCreatedData(BaseModel):
    """Payload for todo.created event."""

    id: UUID = Field(..., description="Unique identifier of the created todo")
    title: str = Field(..., min_length=1, max_length=255, description="Title of the todo")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    completed: bool = Field(default=False, description="Completion status")
    created_at: datetime = Field(..., description="Timestamp when the todo was created")
    actor_id: Optional[str] = Field(None, description="Identifier of the actor who created the todo")


class TodoUpdatedData(BaseModel):
    """Payload for todo.updated event."""

    id: UUID = Field(..., description="Unique identifier of the updated todo")
    changes: dict = Field(..., description="Object containing only the changed fields with new values")
    previous: dict = Field(..., description="Object containing previous values of the changed fields")
    updated_at: datetime = Field(..., description="Timestamp when the update occurred")
    actor_id: Optional[str] = Field(None, description="Identifier of the actor who performed the update")


class TodoCompletedData(BaseModel):
    """Payload for todo.completed event."""

    id: UUID = Field(..., description="Unique identifier of the todo")
    completed: bool = Field(..., description="New completion status (True=completed, False=uncompleted)")
    completed_at: Optional[datetime] = Field(None, description="Timestamp when completed (None if uncompleted)")
    actor_id: Optional[str] = Field(None, description="Identifier of the actor who toggled the status")


class TodoDeletedData(BaseModel):
    """Payload for todo.deleted event."""

    id: UUID = Field(..., description="Unique identifier of the deleted todo")
    title: str = Field(..., description="Title of the deleted todo (for audit purposes)")
    deleted_at: datetime = Field(..., description="Timestamp when the todo was deleted")
    actor_id: Optional[str] = Field(None, description="Identifier of the actor who deleted the todo")


# --------------------
# Agent Domain Events
# --------------------

class AgentActionExecutedData(BaseModel):
    """Payload for agent.action.executed event."""

    action_id: UUID = Field(default_factory=uuid4, description="Unique identifier for this action execution")
    agent_id: str = Field(..., min_length=1, description="Identifier of the AI agent")
    tool_name: str = Field(..., description="Name of the MCP tool that was executed")
    tool_input: dict = Field(..., description="Input parameters passed to the tool")
    tool_output: dict = Field(..., description="Output returned by the tool")
    entity_id: Optional[UUID] = Field(None, description="ID of the affected todo (if applicable)")
    executed_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the action completed")
    duration_ms: int = Field(..., ge=0, description="Execution time in milliseconds")


class AgentActionFailedData(BaseModel):
    """Payload for agent.action.failed event."""

    action_id: UUID = Field(default_factory=uuid4, description="Unique identifier for this action attempt")
    agent_id: str = Field(..., min_length=1, description="Identifier of the AI agent")
    tool_name: str = Field(..., description="Name of the MCP tool that failed")
    tool_input: dict = Field(..., description="Input parameters passed to the tool")
    error_type: str = Field(..., description="Classification of the error")
    error_message: str = Field(..., description="Human-readable error message")
    failed_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the failure occurred")


# --------------------
# Phase V: Reminder & Recurring Events
# --------------------

class ReminderDueData(BaseModel):
    """Payload for reminder.due event."""

    task_id: UUID = Field(..., description="The task ID")
    title: str = Field(..., description="Task title for notification")
    due_at: Optional[datetime] = Field(None, description="When task is due")
    remind_at: datetime = Field(..., description="When to send reminder")
    user_id: str = Field(..., description="User to notify")


class RecurringTaskCreatedData(BaseModel):
    """Payload for todo.recurring.created event."""

    id: UUID = Field(..., description="New task ID")
    parent_id: UUID = Field(..., description="Original recurring task ID")
    title: str = Field(..., description="Task title")
    recurrence_rule: str = Field(..., description="Recurrence pattern")
    due_date: Optional[datetime] = Field(None, description="Next due date")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When created")
