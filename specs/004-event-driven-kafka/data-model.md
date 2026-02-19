# Data Model: Event-Driven Todo Platform

**Feature**: 004-event-driven-kafka
**Date**: 2026-01-23
**Status**: Draft

## Overview

This document defines the data models for the event-driven architecture, including CloudEvents schemas, activity log entities, and the relationship between domain events and their persistence.

---

## Domain Events

### Event Type Hierarchy

```
com.desktoptodo
├── todo
│   ├── created     # New todo created
│   ├── updated     # Todo fields modified
│   ├── completed   # Todo marked complete
│   └── deleted     # Todo removed
└── agent
    ├── action.executed  # AI agent completed action
    └── action.failed    # AI agent action failed
```

### Base CloudEvent Envelope

All events follow CloudEvents v1.0 specification:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `specversion` | string | Yes | Always `"1.0"` |
| `id` | string | Yes | UUID, unique per event |
| `source` | URI | Yes | Publishing service identifier |
| `type` | string | Yes | Event type (reverse-DNS) |
| `time` | timestamp | Yes | ISO 8601 when event occurred |
| `datacontenttype` | string | Yes | Always `"application/json"` |
| `subject` | string | No | Entity ID (e.g., todo UUID) |
| `data` | object | Yes | Domain-specific payload |

---

## Todo Domain Events

### TodoCreatedEvent

**Type**: `com.desktoptodo.todo.created`
**Source**: `/backend/todo-service`

```python
# Pydantic model
class TodoCreatedData(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    completed: bool = False
    created_at: datetime
    actor_id: Optional[str]  # User or service that created
```

**Example**:
```json
{
  "specversion": "1.0",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "source": "/backend/todo-service",
  "type": "com.desktoptodo.todo.created",
  "time": "2026-01-23T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-01-23T10:30:00Z",
    "actor_id": null
  }
}
```

### TodoUpdatedEvent

**Type**: `com.desktoptodo.todo.updated`
**Source**: `/backend/todo-service`

```python
class TodoUpdatedData(BaseModel):
    id: UUID
    changes: dict  # Only changed fields
    previous: dict  # Previous values of changed fields
    updated_at: datetime
    actor_id: Optional[str]
```

**Example**:
```json
{
  "specversion": "1.0",
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "source": "/backend/todo-service",
  "type": "com.desktoptodo.todo.updated",
  "time": "2026-01-23T11:00:00Z",
  "datacontenttype": "application/json",
  "subject": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "changes": {
      "title": "Buy groceries and snacks"
    },
    "previous": {
      "title": "Buy groceries"
    },
    "updated_at": "2026-01-23T11:00:00Z",
    "actor_id": null
  }
}
```

### TodoCompletedEvent

**Type**: `com.desktoptodo.todo.completed`
**Source**: `/backend/todo-service`

```python
class TodoCompletedData(BaseModel):
    id: UUID
    completed: bool  # True when completed, False when uncompleted
    completed_at: Optional[datetime]
    actor_id: Optional[str]
```

**Example**:
```json
{
  "specversion": "1.0",
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "source": "/backend/todo-service",
  "type": "com.desktoptodo.todo.completed",
  "time": "2026-01-23T12:00:00Z",
  "datacontenttype": "application/json",
  "subject": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "completed": true,
    "completed_at": "2026-01-23T12:00:00Z",
    "actor_id": null
  }
}
```

### TodoDeletedEvent

**Type**: `com.desktoptodo.todo.deleted`
**Source**: `/backend/todo-service`

```python
class TodoDeletedData(BaseModel):
    id: UUID
    title: str  # For audit purposes
    deleted_at: datetime
    actor_id: Optional[str]
```

**Example**:
```json
{
  "specversion": "1.0",
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "source": "/backend/todo-service",
  "type": "com.desktoptodo.todo.deleted",
  "time": "2026-01-23T13:00:00Z",
  "datacontenttype": "application/json",
  "subject": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Buy groceries and snacks",
    "deleted_at": "2026-01-23T13:00:00Z",
    "actor_id": null
  }
}
```

---

## Agent Domain Events

### AgentActionExecutedEvent

**Type**: `com.desktoptodo.agent.action.executed`
**Source**: `/agent/mcp-server`

```python
class AgentActionExecutedData(BaseModel):
    action_id: UUID
    agent_id: str
    tool_name: str  # create_todo, update_todo, etc.
    tool_input: dict
    tool_output: dict
    entity_id: Optional[UUID]  # Affected todo ID
    executed_at: datetime
    duration_ms: int
```

**Example**:
```json
{
  "specversion": "1.0",
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "source": "/agent/mcp-server",
  "type": "com.desktoptodo.agent.action.executed",
  "time": "2026-01-23T14:00:00Z",
  "datacontenttype": "application/json",
  "subject": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "data": {
    "action_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "agent_id": "claude-agent-001",
    "tool_name": "create_todo",
    "tool_input": {
      "title": "Schedule meeting",
      "description": "Team sync at 3pm"
    },
    "tool_output": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "success": true
    },
    "entity_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "executed_at": "2026-01-23T14:00:00Z",
    "duration_ms": 150
  }
}
```

### AgentActionFailedEvent

**Type**: `com.desktoptodo.agent.action.failed`
**Source**: `/agent/mcp-server`

```python
class AgentActionFailedData(BaseModel):
    action_id: UUID
    agent_id: str
    tool_name: str
    tool_input: dict
    error_type: str
    error_message: str
    failed_at: datetime
```

---

## Activity Log Entity

### ActivityLog (SQLModel)

Stored in PostgreSQL (Neon), same database as todos.

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
import json

class ActivityLog(SQLModel, table=True):
    __tablename__ = "activity_logs"

    id: int = Field(default=None, primary_key=True)
    event_id: str = Field(unique=True, max_length=255)
    event_type: str = Field(max_length=255, index=True)
    event_source: str = Field(max_length=255)

    entity_type: str = Field(max_length=100)  # "todo" or "agent"
    entity_id: str = Field(max_length=255)

    actor_id: Optional[str] = Field(default=None, max_length=255)
    actor_type: Optional[str] = Field(default=None, max_length=50)

    # JSONB columns for flexible payload storage
    old_data: Optional[str] = Field(default=None)  # JSON string
    new_data: Optional[str] = Field(default=None)  # JSON string
    metadata: Optional[str] = Field(default=None)  # JSON string

    occurred_at: datetime = Field(index=True)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
```

### ProcessedEvent (SQLModel)

For idempotency tracking.

```python
class ProcessedEvent(SQLModel, table=True):
    __tablename__ = "processed_events"

    event_id: str = Field(max_length=255, primary_key=True)
    subscriber_id: str = Field(max_length=255, primary_key=True)
    processed_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Topic Mapping

**Design Decision**: Topic per domain event type (not single topic)

| Topic Name | Event Type | Publisher |
|------------|------------|-----------|
| `todo.created` | `com.desktoptodo.todo.created` | Backend |
| `todo.updated` | `com.desktoptodo.todo.updated` | Backend |
| `todo.completed` | `com.desktoptodo.todo.completed` | Backend |
| `todo.deleted` | `com.desktoptodo.todo.deleted` | Backend |
| `agent.action` | `com.desktoptodo.agent.action.*` | MCP Server |

---

## Entity Relationships

```
┌─────────────────┐     publishes     ┌─────────────────────────┐
│  Todo Service   │──────────────────▶│   Kafka Topics          │
│  (backend)      │                   │  ├── todo.created       │
└─────────────────┘                   │  ├── todo.updated       │
                                      │  ├── todo.completed     │
┌─────────────────┐     publishes     │  ├── todo.deleted       │
│   MCP Server    │──────────────────▶│  └── agent.action       │
│    (agent)      │                   └───────────┬─────────────┘
└─────────────────┘                               │
                                                  │ subscribes (all topics)
                                                  ▼
                                      ┌─────────────────┐
                                      │ Activity Logger │
                                      │   (stateless)   │
                                      └────────┬────────┘
                                               │ writes
                                               ▼
                                      ┌─────────────────┐
                                      │   PostgreSQL    │
                                      │ (activity_logs) │
                                      └─────────────────┘
```

---

## Validation Rules

### CloudEvent Envelope
- `id`: Must be valid UUID v4
- `source`: Must start with `/`
- `type`: Must match `com.desktoptodo.*` pattern
- `time`: Must be valid ISO 8601 timestamp
- `data`: Must be valid JSON object

### Todo Event Data
- `id`: Must be valid UUID v4
- `title`: 1-255 characters (when present)
- `description`: 0-1000 characters (optional)
- `completed`: Boolean
- `actor_id`: Optional, max 255 characters

### Agent Event Data
- `action_id`: Must be valid UUID v4
- `agent_id`: Non-empty string
- `tool_name`: Must be known tool (create_todo, update_todo, delete_todo, toggle_todo, list_todos)
- `duration_ms`: Non-negative integer

---

## Schema Evolution

### Adding Fields (Non-Breaking)
- Add new optional fields to `data` payload
- Consumers must ignore unknown fields
- No type versioning required

### Removing/Renaming Fields (Breaking)
- Create new event type with `.v2` suffix
- Produce both versions during migration period
- Deprecate old version after consumers migrate

### Example Migration
```
Phase 1: Produce com.desktoptodo.todo.created (v1 only)
Phase 2: Produce both v1 and com.desktoptodo.todo.created.v2
Phase 3: Consumers migrate to v2
Phase 4: Stop producing v1
```
