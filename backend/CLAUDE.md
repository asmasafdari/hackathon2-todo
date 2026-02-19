# Backend Guidelines

## Stack
- FastAPI
- SQLModel (ORM)
- Neon PostgreSQL
- Dapr for event publishing

## Project Structure
- `main.py` - FastAPI app entry point
- `models/` - SQLModel database models (todo, user, conversation, message)
- `routers/` - API route handlers (todos, chat)
- `services/` - Business logic (todo_service, chat_service, conversation_service, event_publisher)
- `events/` - CloudEvents schemas
- `database.py` - Database connection and session management
- `migrations/` - Alembic database migrations
- `tests/` - Pytest test suite

## API Conventions
- All routes under `/api/`
- Return JSON responses
- Use Pydantic/SQLModel schemas for request/response
- Handle errors with HTTPException

## Database
- Use SQLModel for all database operations
- Connection string from environment variable: DATABASE_URL
- UUID primary keys on all models

## Running
```bash
cd backend && uvicorn main:app --reload --port 8000
```
