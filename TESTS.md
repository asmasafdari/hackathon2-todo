# Test Suite Documentation

Complete test coverage for all Todo Platform services.

## Test Structure

```
backend/tests/           # Backend API and service tests
├── conftest.py         # Test fixtures and configuration
├── test_todos.py       # API endpoint tests
├── test_todo_service.py # Business logic tests
├── test_event_publisher.py # Event publishing tests
├── test_events.py      # CloudEvent schema tests
└── README.md           # Backend testing guide

agent/tests/            # AI Agent tests
├── conftest.py         # Test fixtures
├── test_mcp_server.py  # MCP tool tests
├── test_event_publisher.py # Event publishing tests
└── __init__.py

activity-logger/tests/  # Activity Logger tests
├── conftest.py         # Test fixtures
├── test_event_handler.py # Event processing tests
└── test_logs_router.py  # API endpoint tests
```

## Running Tests

### Backend Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_todos.py

# Run specific test class
pytest tests/test_todos.py::TestCreateTodo

# Run specific test
pytest tests/test_todos.py::TestCreateTodo::test_create_todo_success

# Verbose output
pytest -v
```

### Agent Tests

```bash
cd agent

# Install test dependencies
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v
```

### Activity-Logger Tests

```bash
cd activity-logger

# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=activity_logger --cov-report=html
```

### All Services

```bash
# Run from project root

# Backend
cd backend && pytest && cd ..

# Agent
cd agent && pytest tests/ && cd ..

# Activity Logger
cd activity-logger && pytest tests/ && cd ..
```

## Test Coverage

### Backend Tests

**test_todos.py** - API Endpoint Tests
- ✅ `TestCreateTodo` - POST /api/todos
  - Create todo with valid data
  - Create without description
  - Empty title validation
  - Missing title validation
  
- ✅ `TestListTodos` - GET /api/todos
  - Empty list
  - List with items
  - Ordering
  
- ✅ `TestGetTodo` - GET /api/todos/{id}
  - Get existing todo
  - Not found (404)
  - Invalid ID format
  
- ✅ `TestUpdateTodo` - PUT /api/todos/{id}
  - Update title
  - Update description
  - Update both fields
  - Not found (404)
  - No fields provided
  
- ✅ `TestToggleTodo` - PATCH /api/todos/{id}/toggle
  - Toggle to completed
  - Toggle to incomplete
  - Not found (404)
  
- ✅ `TestDeleteTodo` - DELETE /api/todos/{id}
  - Delete success
  - Not found (404)
  - Invalid ID format
  
- ✅ `TestHealthEndpoint` - GET /health
  - Health check response

**test_todo_service.py** - Business Logic Tests
- ✅ `TestTodoService`
  - Create todo
  - Get all todos (empty and with items)
  - Get todo by ID
  - Update todo
  - Toggle todo
  - Delete todo
  - All not-found scenarios

**test_event_publisher.py** - Event Publishing Tests
- ✅ `TestEventPublisher`
  - Default initialization
  - Custom pubsub name
  - Publish todo.created event
  - Publish todo.updated event
  - Publish todo.completed event
  - Publish todo.deleted event
  - Handle publish failures
- ✅ `TestEventPublisherSingleton`
  - Singleton exists
  - Default pubsub name

**test_events.py** - CloudEvent Schema Tests
- ✅ `TestCloudEventEnvelope`
  - Create minimal event
  - Create full event
  - Source validation (must start with /)
  - Type validation (must follow pattern)
  - Convert to dict
  - Handle Pydantic model data
- ✅ `TestTodoCreatedData`
  - Create minimal/full data
  - Title length validation
- ✅ `TestTodoUpdatedData`
  - Create with changes/previous
- ✅ `TestTodoCompletedData`
  - Completed and uncompleted states
- ✅ `TestTodoDeletedData`
  - Create with metadata
- ✅ `TestAgentActionExecutedData`
  - Create with all fields
  - Default action_id
  - Duration validation
- ✅ `TestAgentActionFailedData`
  - Create with error info
  - Default action_id

### Agent Tests

**test_mcp_server.py** - MCP Tool Tests
- ✅ `TestCreateTodo`
  - Success with description
  - Success without description
  - Connection error handling
  - API error handling
  - Event publishing (success/failure)
  
- ✅ `TestListTodos`
  - List all
  - Filter pending
  - Filter completed
  - Event publishing
  
- ✅ `TestGetTodo`
  - Success
  - Not found
  - Event publishing
  
- ✅ `TestUpdateTodo`
  - Success
  - No fields validation
  - Not found
  - Event publishing
  
- ✅ `TestToggleTodo`
  - Success
  - Not found
  - Event publishing
  
- ✅ `TestDeleteTodo`
  - Success
  - Not found
  - Timeout handling
  - Event publishing

**test_event_publisher.py** - Agent Event Publishing Tests
- ✅ `TestEventPublisher`
  - Default initialization
  - Custom Dapr port from env
  - CloudEvent creation
  - CloudEvent auto ID generation
  - Publish event success
  - Publish event failure handling
  - Publish event exception handling
  - Publish agent.action.executed
  - Publish agent.action.failed
- ✅ `TestGetEventPublisher`
  - Singleton pattern
  - Same instance across calls

### Activity-Logger Tests

**test_event_handler.py** - Event Processing Tests
- ✅ `TestEventHandler`
  - Is already processed (false)
  - Is already processed (true)
  - Process event success
  - Process event idempotent
  - Invalid timestamp handling
  - No todo_id in data

**test_logs_router.py** - API Tests
- ✅ `TestListLogs`
  - Create and retrieve log
  
- ✅ `TestLogFiltering`
  - Filter by event type
  - Filter by todo ID
  
- ✅ `TestLogStats`
  - Get statistics
  
- ✅ `TestIdempotency`
  - Processed event tracking

## Test Fixtures

### Backend Fixtures (conftest.py)

- `event_loop` - Async event loop for tests
- `test_engine` - In-memory SQLite database engine
- `test_session` - Database session for service tests
- `client` - HTTPX async client for API tests
- `sample_todo` - Pre-created todo for dependent tests

### Agent Fixtures (conftest.py)

- `sample_todo` - Sample todo dict
- `sample_todo_completed` - Completed todo dict
- `sample_todos` - List of sample todos
- `mock_http_client` - Mock HTTPX client
- `mock_response_factory` - Factory for mock responses

### Activity-Logger Fixtures (conftest.py)

- `event_loop` - Async event loop
- `test_engine` - In-memory SQLite engine
- `test_session` - Database session

## Writing New Tests

### Backend Test Pattern

```python
class TestNewFeature:
    """Tests for new feature."""
    
    async def test_success_case(self, client: AsyncClient):
        """Test successful operation."""
        response = await client.post("/api/endpoint", json={"data": "value"})
        
        assert response.status_code == 201
        data = response.json()
        assert data["field"] == "expected"
    
    async def test_error_case(self, client: AsyncClient):
        """Test error handling."""
        response = await client.post("/api/endpoint", json={"invalid": "data"})
        
        assert response.status_code == 422
```

### Agent Test Pattern

```python
class TestNewTool:
    """Tests for new MCP tool."""
    
    @patch('mcp_server.get_http_client')
    def test_success(self, mock_get_client, mock_response_factory):
        """Test successful tool execution."""
        response = mock_response_factory(200, {"result": "success"})
        
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = response
        mock_get_client.return_value = mock_client
        
        result = new_tool("param")
        
        assert result["result"] == "success"
```

## Continuous Integration

Add to your CI/CD pipeline:

```yaml
# GitHub Actions example
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install backend dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio httpx
    
    - name: Run backend tests
      run: |
        cd backend
        pytest
    
    - name: Install agent dependencies
      run: |
        cd agent
        pip install -r requirements.txt
        pip install pytest
    
    - name: Run agent tests
      run: |
        cd agent
        pytest tests/
```

## Troubleshooting

### Database locked errors
```bash
# Use --forked to run tests in separate processes
pytest --forked
```

### Async test failures
```bash
# Make sure pytest-asyncio is installed
pip install pytest-asyncio
```

### Import errors
```bash
# Install packages in editable mode
pip install -e .
```

## Best Practices

1. **Use fixtures** - Don't repeat setup code
2. **Test edge cases** - Empty inputs, invalid data, not found
3. **Mock external services** - Don't call real APIs in tests
4. **Clean up after tests** - Use transaction rollback
5. **Use descriptive names** - Test names should explain what they test
6. **Group related tests** - Use classes to organize
7. **Keep tests fast** - Use in-memory databases, mock slow operations
