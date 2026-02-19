# Backend Tests

## Running Tests

### Install Test Dependencies

```bash
cd backend
pip install pytest pytest-asyncio httpx
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=backend --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_todos.py
```

### Run Specific Test Class

```bash
pytest tests/test_todos.py::TestCreateTodo
```

### Run Specific Test

```bash
pytest tests/test_todos.py::TestCreateTodo::test_create_todo_success
```

### Run in Verbose Mode

```bash
pytest -v
```

## Test Structure

- **test_todos.py** - API endpoint tests
- **test_todo_service.py** - Business logic tests
- **conftest.py** - Test fixtures and configuration

## Fixtures

- `client` - Async HTTP client for API testing
- `test_session` - Database session for service testing
- `sample_todo` - Pre-created todo for dependent tests

## Test Database

Tests use an in-memory SQLite database that is recreated for each test session.
