"""
Events module for the Todo platform.

This module provides CloudEvents-based event publishing via Dapr pub/sub.
"""

from .types import (
    EVENT_TODO_CREATED,
    EVENT_TODO_UPDATED,
    EVENT_TODO_COMPLETED,
    EVENT_TODO_DELETED,
    EVENT_AGENT_ACTION_EXECUTED,
    EVENT_AGENT_ACTION_FAILED,
    TOPIC_TODO_CREATED,
    TOPIC_TODO_UPDATED,
    TOPIC_TODO_COMPLETED,
    TOPIC_TODO_DELETED,
    TOPIC_AGENT_ACTION,
)
from .schemas import (
    CloudEventEnvelope,
    TodoCreatedData,
    TodoUpdatedData,
    TodoCompletedData,
    TodoDeletedData,
)

__all__ = [
    # Event types
    "EVENT_TODO_CREATED",
    "EVENT_TODO_UPDATED",
    "EVENT_TODO_COMPLETED",
    "EVENT_TODO_DELETED",
    "EVENT_AGENT_ACTION_EXECUTED",
    "EVENT_AGENT_ACTION_FAILED",
    # Topics
    "TOPIC_TODO_CREATED",
    "TOPIC_TODO_UPDATED",
    "TOPIC_TODO_COMPLETED",
    "TOPIC_TODO_DELETED",
    "TOPIC_AGENT_ACTION",
    # Schemas
    "CloudEventEnvelope",
    "TodoCreatedData",
    "TodoUpdatedData",
    "TodoCompletedData",
    "TodoDeletedData",
]
