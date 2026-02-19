# Research: Event-Driven Architecture with Dapr and Kafka

**Feature**: 004-event-driven-kafka
**Date**: 2026-01-23
**Status**: Complete

## Summary

This document captures research findings for implementing an event-driven architecture using Dapr pub/sub with Apache Kafka as the message broker. All unknowns from the Technical Context have been resolved.

---

## 1. Dapr Pub/Sub with Kafka in Python

### Decision: Use dapr-client SDK with FastAPI extension

### Rationale
- Dapr provides a broker-agnostic pub/sub API
- Python SDK integrates cleanly with FastAPI via `dapr-ext-fastapi`
- CloudEvents format is natively supported

### Kafka Pub/Sub Component Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka.default.svc.cluster.local:9092"
    - name: authType
      value: "none"  # Dev; use password/mtls in production
    - name: consumerGroup
      value: "{namespace}-{appId}"
    - name: maxMessageBytes
      value: "1048576"
scopes:
  - todo-backend
  - activity-logger
```

### Publishing Events (Python)

```python
from dapr.clients import DaprClient
import json

async def publish_event(pubsub_name: str, topic: str, event_data: dict):
    with DaprClient() as client:
        client.publish_event(
            pubsub_name=pubsub_name,
            topic_name=topic,
            data=json.dumps(event_data),
            data_content_type="application/cloudevents+json",
        )
```

### Subscribing in FastAPI

```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="kafka-pubsub", topic="todo-events")
async def handle_event(event: dict):
    # Process event
    return {"status": "SUCCESS"}
```

### Alternatives Considered
- **Direct Kafka client (aiokafka)**: Rejected per constraint TC-004 (no direct Kafka usage)
- **Celery with Kafka**: Overkill for simple event publishing

---

## 2. CloudEvents Specification

### Decision: CloudEvents v1.0 with type-based versioning

### Rationale
- Industry standard for event format
- Native support in Dapr pub/sub
- Python SDK available (`cloudevents` package)

### Required Fields

| Attribute | Type | Example |
|-----------|------|---------|
| `id` | String (UUID) | `"550e8400-e29b-41d4-a716-446655440000"` |
| `source` | URI-reference | `"/backend/todo-service"` |
| `specversion` | String | `"1.0"` |
| `type` | String (reverse-DNS) | `"com.desktoptodo.todo.created"` |

### Recommended Optional Fields

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `time` | Event timestamp | `"2026-01-23T10:30:00Z"` |
| `datacontenttype` | Payload MIME type | `"application/json"` |
| `subject` | Entity ID | `"todo-123"` |

### Schema Versioning Strategy

Use type-based versioning for breaking changes:
- `com.desktoptodo.todo.created` (v1, implicit)
- `com.desktoptodo.todo.created.v2` (v2, breaking change)

For non-breaking changes, consumers ignore unknown fields.

### Alternatives Considered
- **Avro with Schema Registry**: Rejected (out of scope, adds complexity)
- **Custom JSON format**: Rejected (CloudEvents provides better tooling)

---

## 3. Idempotent Event Handlers

### Decision: Inbox table pattern with database constraints

### Rationale
- Durable deduplication (survives service restarts)
- Simple to implement with SQLModel
- Works with existing PostgreSQL (Neon)

### Schema

```sql
CREATE TABLE processed_events (
    event_id VARCHAR(255) NOT NULL,
    subscriber_id VARCHAR(255) NOT NULL,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (event_id, subscriber_id)
);
```

### Implementation Pattern

```python
async def handle_event_idempotently(db: AsyncSession, event_id: str, subscriber_id: str, process_fn):
    try:
        async with db.begin():
            # Insert first (fails on duplicate)
            await db.execute(
                text("INSERT INTO processed_events (event_id, subscriber_id) VALUES (:e, :s)"),
                {"e": event_id, "s": subscriber_id}
            )
            await process_fn()  # Only if insert succeeds
    except IntegrityError:
        return {"status": "DUPLICATE"}
    return {"status": "PROCESSED"}
```

### Alternatives Considered
- **Redis deduplication cache**: Rejected (requires additional infrastructure)
- **Kafka consumer offsets only**: Rejected (doesn't protect against reprocessing after rollback)

---

## 4. Dapr on Kubernetes

### Decision: Sidecar injection with health check integration

### Rationale
- Standard Kubernetes deployment pattern for Dapr
- Automatic sidecar lifecycle management
- Built-in health probes

### Required Annotations

```yaml
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "todo-backend"
    dapr.io/app-port: "8000"
    dapr.io/app-protocol: "http"
    dapr.io/sidecar-cpu-limit: "300m"
    dapr.io/sidecar-memory-limit: "256Mi"
    dapr.io/enable-app-health-check: "true"
    dapr.io/app-health-check-path: "/health"
```

### Startup Order Handling

Application waits for Dapr sidecar before processing:

```python
async def wait_for_dapr(max_retries: int = 30):
    dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
    for _ in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"http://localhost:{dapr_port}/v1.0/healthz")
                if resp.status_code == 204:
                    return
        except Exception:
            pass
        await asyncio.sleep(1)
    raise RuntimeError("Dapr sidecar not ready")
```

### Component Deployment Order
1. Deploy Dapr components (pubsub.yaml)
2. Deploy Kafka (if in-cluster)
3. Deploy application pods (sidecar injected automatically)

### Alternatives Considered
- **Init containers**: Rejected (adds complexity, slower startup)
- **Manual sidecar configuration**: Rejected (loses auto-injection benefits)

---

## 5. Activity Log Schema Design

### Decision: Single table with JSONB payload and strategic indexes

### Rationale
- Flexible schema supports all event types
- JSONB enables querying within payload
- Strategic indexing covers common query patterns

### Schema

```sql
CREATE TABLE activity_logs (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL UNIQUE,
    event_type VARCHAR(255) NOT NULL,
    event_source VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    actor_id VARCHAR(255),
    actor_type VARCHAR(50),
    old_data JSONB,
    new_data JSONB,
    metadata JSONB,
    occurred_at TIMESTAMPTZ NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Indexes

```sql
-- Time-range queries
CREATE INDEX idx_activity_occurred_at ON activity_logs(occurred_at DESC);

-- Entity queries
CREATE INDEX idx_activity_entity ON activity_logs(entity_type, entity_id, occurred_at DESC);

-- Event type queries
CREATE INDEX idx_activity_type_time ON activity_logs(event_type, occurred_at DESC);
```

### Alternatives Considered
- **Partitioned tables**: Rejected for Phase V (insufficient volume to justify)
- **Separate event store (EventStoreDB)**: Rejected (out of scope, adds infrastructure)

---

## Sources

- [Dapr Kafka Pub/Sub Component](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [Dapr Python SDK FastAPI Extension](https://docs.dapr.io/developing-applications/sdks/python/python-sdk-extensions/python-fastapi/)
- [CloudEvents Specification v1.0](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md)
- [Idempotent Consumer Pattern](https://microservices.io/patterns/communication-style/idempotent-consumer.html)
- [Dapr Kubernetes Annotations](https://docs.dapr.io/reference/arguments-annotations-overview/)

---

## 6. Topic Strategy

### Decision: Topic per domain event type

### Rationale
- Better isolation between event types
- Easier to scale consumers per event type
- Simpler subscription management in Dapr
- Cleaner dead-letter handling per topic

### Topic Mapping

| Topic Name | Event Type | Publisher |
|------------|------------|-----------|
| `todo.created` | `com.desktoptodo.todo.created` | Backend |
| `todo.updated` | `com.desktoptodo.todo.updated` | Backend |
| `todo.completed` | `com.desktoptodo.todo.completed` | Backend |
| `todo.deleted` | `com.desktoptodo.todo.deleted` | Backend |
| `agent.action` | `com.desktoptodo.agent.action.*` | MCP Server |

### Consumer Subscriptions

Activity Logger subscribes to all topics:

```python
@dapr_app.subscribe(pubsub="kafka-pubsub", topic="todo.created")
@dapr_app.subscribe(pubsub="kafka-pubsub", topic="todo.updated")
@dapr_app.subscribe(pubsub="kafka-pubsub", topic="todo.completed")
@dapr_app.subscribe(pubsub="kafka-pubsub", topic="todo.deleted")
@dapr_app.subscribe(pubsub="kafka-pubsub", topic="agent.action")
async def handle_event(event: dict):
    # Unified handler for all event types
    return {"status": "SUCCESS"}
```

### Alternatives Considered
- **Single topic with event type filtering**: Rejected (harder to scale, all events share throughput)
- **Topic per entity ID**: Rejected (excessive topic count, unnecessary for Phase V)

---

## Resolved Unknowns

| Unknown | Resolution |
|---------|------------|
| Dapr pub/sub configuration | Kafka component with scopes for app isolation |
| CloudEvents versioning | Type-based versioning (e.g., `.v2` suffix) |
| Idempotency approach | Inbox table with INSERT-before-process pattern |
| Sidecar startup order | Wait-for-dapr function in app startup |
| Activity log schema | JSONB-based with strategic indexes |
| Topic strategy | Topic per domain event type |
