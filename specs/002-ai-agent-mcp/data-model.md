# Data Model: AI Agent-Driven Todo Management

**Feature**: 002-ai-agent-mcp
**Date**: 2026-01-22

## Overview

Phase III does not introduce new persistent data models. The agent layer works with existing Phase II entities via REST API. This document defines the **agent-layer entities** and **message structures**.

## Existing Entities (Phase II - via API)

Reference: [Phase II Data Model](../001-fullstack-todo/data-model.md)

### Todo (from Phase II API)

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| title | string (1-255) | Task title |
| description | string (0-1000) | Optional description |
| completed | boolean | Completion status |
| created_at | datetime | Creation timestamp |

## New Agent-Layer Entities

### ConversationSession

Represents a user's chat session with the agent.

| Field | Type | Description |
|-------|------|-------------|
| session_id | string | Unique session identifier |
| created_at | datetime | Session start time |
| last_active | datetime | Last interaction time |
| message_count | integer | Number of messages in session |

**Storage**: SQLite via `SQLiteSession` (OpenAI Agents SDK)

**Lifecycle**:
- Created when user starts CLI
- Persisted between CLI invocations (same session_id)
- Cleared on explicit reset or session expiry

### ConversationMessage

Individual message in a conversation.

| Field | Type | Description |
|-------|------|-------------|
| role | enum | "user" or "assistant" |
| content | string | Message text |
| timestamp | datetime | Message time |
| tool_calls | array | Optional tool invocations |

**Storage**: Part of session state (managed by SDK)

### ToolCall

Record of an MCP tool invocation.

| Field | Type | Description |
|-------|------|-------------|
| tool_name | string | Name of the tool called |
| arguments | object | Parameters passed |
| result | object/string | Tool return value |
| is_error | boolean | Whether tool returned error |
| timestamp | datetime | Invocation time |

**Storage**: Ephemeral (part of agent execution trace)

## MCP Tool Schemas

### create_todo

```json
{
  "name": "create_todo",
  "description": "Create a new todo item. Use when the user wants to add a task.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 255,
        "description": "The title of the todo item (required)"
      },
      "description": {
        "type": "string",
        "maxLength": 1000,
        "description": "Optional detailed description"
      }
    },
    "required": ["title"]
  }
}
```

### list_todos

```json
{
  "name": "list_todos",
  "description": "List all todos with optional filtering. Use to show the user their tasks.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "filter": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "default": "all",
        "description": "Filter todos by status"
      }
    },
    "required": []
  }
}
```

### get_todo

```json
{
  "name": "get_todo",
  "description": "Get details of a specific todo by ID.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "format": "uuid",
        "description": "The UUID of the todo to retrieve"
      }
    },
    "required": ["id"]
  }
}
```

### update_todo

```json
{
  "name": "update_todo",
  "description": "Update an existing todo's title or description.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "format": "uuid",
        "description": "The UUID of the todo to update"
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 255,
        "description": "New title (optional)"
      },
      "description": {
        "type": "string",
        "maxLength": 1000,
        "description": "New description (optional)"
      }
    },
    "required": ["id"]
  }
}
```

### toggle_todo

```json
{
  "name": "toggle_todo",
  "description": "Toggle a todo's completion status. Complete becomes incomplete and vice versa.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "format": "uuid",
        "description": "The UUID of the todo to toggle"
      }
    },
    "required": ["id"]
  }
}
```

### delete_todo

```json
{
  "name": "delete_todo",
  "description": "Permanently delete a todo. This action cannot be undone.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "format": "uuid",
        "description": "The UUID of the todo to delete"
      }
    },
    "required": ["id"]
  }
}
```

## Data Flow

```
User Input (natural language)
    ↓
Agent (interprets intent)
    ↓
Tool Call (structured JSON)
    ↓
MCP Server (validates, forwards)
    ↓
REST API (processes request)
    ↓
Response (JSON)
    ↓
Tool Result (back to agent)
    ↓
Agent Response (natural language)
```

## Validation Rules

### Input Validation (MCP Layer)

| Tool | Validation |
|------|------------|
| create_todo | title required, 1-255 chars |
| list_todos | filter must be all/pending/completed |
| get_todo | id must be valid UUID |
| update_todo | at least one of title/description required |
| toggle_todo | id must be valid UUID |
| delete_todo | id must be valid UUID |

### Error States

| Error Type | Source | User Message |
|------------|--------|--------------|
| Invalid params | MCP validation | "Please provide a valid [field]" |
| Todo not found | API 404 | "I couldn't find a todo with that ID" |
| API unavailable | HTTP error | "I'm having trouble reaching the todo service" |
| Unknown intent | Agent | "I'm not sure what you'd like me to do. Could you clarify?" |

## State Transitions

### Todo Completion State

```
[Created] → completed=false (pending)
    ↓ toggle_todo
[Completed] → completed=true
    ↓ toggle_todo
[Pending] → completed=false
```

### Session State

```
[New] → session created
    ↓ user message
[Active] → messages accumulating
    ↓ user message
[Active] → context preserved
    ↓ session reset/expiry
[Cleared] → context lost
```
