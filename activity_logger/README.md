# Activity Logger Service

FastAPI service that consumes todo events via Dapr pub/sub and provides an audit trail API.

## Features

- Subscribes to all todo events (created, updated, completed, deleted)
- Idempotent event processing (no duplicates)
- REST API for querying activity logs
- PostgreSQL persistence
- CloudEvents format support

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run the service
uvicorn main:app --reload --port 8081
```

## API Endpoints

- `GET /health` - Health check
- `GET /logs` - Query activity logs (with filters)
- `GET /logs/{event_id}` - Get specific log entry
- `GET /logs/stats` - Get statistics

## Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host/db
DAPR_HTTP_PORT=3500
```

## Event Consumption

This service consumes events via Dapr pub/sub:
- `todo.created`
- `todo.updated`
- `todo.completed`
- `todo.deleted`

Events are stored with full payload for audit trail.
