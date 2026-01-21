# Data Model: Phase II - Fullstack Todo Application

**Feature**: 001-fullstack-todo
**Date**: 2026-01-21

---

## Entities

### Todo

Primary entity representing a task item.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| title | string | NOT NULL, max 255 chars | Task title |
| description | string | NULLABLE, max 1000 chars | Optional detailed description |
| completed | boolean | NOT NULL, default: false | Completion status |
| created_at | timestamp | NOT NULL, auto-generated | Creation timestamp (UTC) |

**Indexes**:
- Primary key on `id`
- Index on `created_at` (for ordering)

---

## Database Schema (PostgreSQL)

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
```

---

## SQLModel Definition

```python
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import SQLModel, Field

class TodoBase(SQLModel):
    """Shared fields for Todo (used in create/update)"""
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

class Todo(TodoBase, table=True):
    """Database model for Todo"""
    __tablename__ = "todos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TodoCreate(TodoBase):
    """Schema for creating a new Todo"""
    pass

class TodoUpdate(SQLModel):
    """Schema for updating a Todo (all fields optional)"""
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

class TodoRead(TodoBase):
    """Schema for reading a Todo (API response)"""
    id: UUID
    completed: bool
    created_at: datetime
```

---

## State Transitions

```
                    ┌─────────────┐
                    │   CREATE    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
         ┌─────────│   PENDING   │─────────┐
         │         └──────┬──────┘         │
         │                │                │
      UPDATE           TOGGLE           DELETE
         │                │                │
         │                ▼                │
         │         ┌─────────────┐         │
         └────────▶│  COMPLETED  │─────────┤
                   └──────┬──────┘         │
                          │                │
                       TOGGLE              │
                          │                │
                          ▼                ▼
                   ┌─────────────┐   ┌─────────────┐
                   │   PENDING   │   │   DELETED   │
                   └─────────────┘   └─────────────┘
```

**State Rules**:
- New todos always start as `completed: false`
- Toggle switches between `completed: true` and `completed: false`
- Delete is terminal (hard delete, no soft delete)
- Update does not change completion status (use toggle for that)

---

## Validation Rules

### Title
- Required (cannot be empty or null)
- Maximum 255 characters
- Whitespace-only strings rejected
- Leading/trailing whitespace trimmed

### Description
- Optional (can be null or empty)
- Maximum 1000 characters
- Leading/trailing whitespace trimmed

### ID
- Must be valid UUID format
- Auto-generated on creation
- Immutable after creation

### Completed
- Boolean only (true/false)
- Defaults to false on creation
- Changed only via toggle operation

### Created At
- Auto-generated on creation
- Immutable after creation
- Stored in UTC timezone

---

## Relationships

None - Todo is a standalone entity with no foreign keys.

---

## Frontend Type Definitions (TypeScript)

```typescript
interface Todo {
  id: string;           // UUID as string
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;   // ISO 8601 timestamp
}

interface TodoCreate {
  title: string;
  description?: string;
}

interface TodoUpdate {
  title?: string;
  description?: string;
}
```
