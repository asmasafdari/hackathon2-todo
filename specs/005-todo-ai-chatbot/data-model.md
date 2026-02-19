# Data Model: Todo AI Chatbot

**Date**: 2026-02-16
**Feature**: 005-todo-ai-chatbot

## Entities

All models already exist in `backend/models/`. No schema changes required.

### User

**File**: `backend/models/user.py`

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | |
| email | string | Unique, required | |
| name | string | Optional | |
| is_active | boolean | Default: true | |
| hashed_password | string | Default: "clerk-managed" | Clerk handles auth |
| created_at | datetime | Auto, UTC | |
| updated_at | datetime | Auto, UTC | |

**Relationships**: Has many Todos, Conversations, Messages

### Todo (Task)

**File**: `backend/models/todo.py`

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | |
| user_id | UUID | FK → User.id, required | |
| title | string | Required, max 255 chars | Non-empty validated |
| description | string | Optional | |
| completed | boolean | Default: false | |
| created_at | datetime | Auto, UTC | |
| updated_at | datetime | Auto, UTC | |

**State transitions**: pending → completed (via toggle endpoint)

### Conversation

**File**: `backend/models/conversation.py`

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | |
| user_id | UUID | FK → User.id, required | |
| title | string | Optional | |
| created_at | datetime | Auto, UTC | |
| updated_at | datetime | Auto, UTC | |

**Relationships**: Has many Messages, belongs to User

### Message

**File**: `backend/models/message.py`

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | |
| conversation_id | UUID | FK → Conversation.id, required | |
| user_id | UUID | FK → User.id, required | |
| role | string | Enum: user, assistant, system | |
| content | string | Required | |
| tool_calls | string (JSON) | Optional | Serialized JSON array of ToolCall |
| created_at | datetime | Auto, UTC | |

**Relationships**: Belongs to Conversation, belongs to User

## ToolCall Schema (embedded in Message.tool_calls)

```json
{
  "tool": "add_task",
  "parameters": {"user_id": "...", "title": "..."},
  "result": {"task_id": "5", "status": "created", "title": "Buy groceries"}
}
```

## Entity Relationship Diagram

```
User (1) ──── (*) Todo
  │
  └── (1) ──── (*) Conversation
                      │
                      └── (1) ──── (*) Message
```

## Indexes (Recommended)

- `Todo.user_id` — Filter todos by user
- `Conversation.user_id` — Filter conversations by user
- `Message.conversation_id` — Fetch messages for conversation
- `Message.created_at` — Order messages chronologically
