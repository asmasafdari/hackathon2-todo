# Event-Driven Architecture

This document describes the event-driven architecture using Kafka and Dapr.

## Architecture Overview

```
┌──────────────┐     Events      ┌─────────────┐
│   Backend    │ ───────────────▶ │    Kafka    │
│  (FastAPI)   │                  │   (Dapr)    │
└──────────────┘                  └──────┬──────┘
                                         │
┌──────────────┐     Events      ┌──────▼──────┐
│     MCP      │ ───────────────▶ │   Topics    │
│  (AI Agent)  │                  │             │
└──────────────┘                  └──────┬──────┘
                                         │
                              ┌──────────┼──────────┐
                              │          │          │
                         ┌────▼───┐ ┌────▼───┐ ┌───▼────┐
                         │ Logger │ │Analytics│ │Notifications│
                         └────────┘ └────────┘ └────────┘
```

## Event Flow

### 1. Todo Created
```
User → Frontend → Backend → Dapr → Kafka (todo-created topic)
                                               ↓
                                      Activity Logger (persist)
```

### 2. Todo Updated
```
User → Frontend → Backend → Dapr → Kafka (todo-updated topic)
                                               ↓
                                      Activity Logger (persist)
```

### 3. Agent Action
```
User → CLI → Agent → MCP Tool → Backend API (success/failure)
                                   ↓
                              Dapr → Kafka (agent-action-* topic)
                                               ↓
                                      Activity Logger (persist)
```

## Event Schema (CloudEvents)

All events follow the CloudEvents v1.0 specification:

```json
{
  "specversion": "1.0",
  "type": "com.desktoptodo.todo.created",
  "source": "/backend/todos",
  "id": "unique-event-id",
  "time": "2026-01-22T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "id": "todo-uuid",
    "title": "Todo Title",
    "description": "Todo Description",
    "completed": false,
    "created_at": "2026-01-22T10:00:00Z"
  }
}
```

## Event Types

| Event Type | Source | Data Schema | Description |
|------------|--------|-------------|-------------|
| `com.desktoptodo.todo.created` | /backend/todos | Todo object | Todo was created |
| `com.desktoptodo.todo.updated` | /backend/todos | Todo object | Todo was updated |
| `com.desktoptodo.todo.completed` | /backend/todos | Todo object | Todo was marked complete |
| `com.desktoptodo.todo.deleted` | /backend/todos | `{id, deleted_at}` | Todo was deleted |
| `com.desktoptodo.agent.action.executed` | /agent/mcp | `{tool, params, result}` | Agent action success |
| `com.desktoptodo.agent.action.failed` | /agent/mcp | `{tool, params, error}` | Agent action failure |

## Dapr Integration

### Publisher Side

Backend services publish events using Dapr pub/sub:

```python
from dapr.clients import DaprClient

with DaprClient() as client:
    client.publish_event(
        pubsub_name="todo-pubsub",
        topic_name="todo-created",
        data=json.dumps(event_data),
        data_content_type="application/json",
    )
```

### Subscriber Side

Activity logger subscribes to events:

```python
from dapr.ext.fastapi import DaprApp

dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="todo-pubsub", topic="todo-created")
async def handle_todo_created(event_data: dict):
    # Process event
    pass
```

## Deployment

1. Deploy Kafka: See KAFKA.md
2. Deploy Dapr: `dapr init -k`
3. Deploy Dapr component: Included in Helm chart
4. Deploy services with Dapr sidecars

## Monitoring

### View Events
```bash
# Check Kafka topics
kubectl exec -it -n todo kafka-0 -- kafka-topics.sh --list --bootstrap-server localhost:9092

# View event counts
kubectl exec -it -n todo kafka-0 -- kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic todo-created
```

### Dapr Dashboard
```bash
dapr dashboard -k
```

### Check Logs
```bash
# Backend publisher logs
kubectl logs -n todo deployment/todo-platform-backend -c backend

# Activity logger consumer logs
kubectl logs -n todo deployment/todo-platform-activity-logger -c activity-logger

# Dapr sidecar logs
kubectl logs -n todo deployment/todo-platform-backend -c daprd
```
