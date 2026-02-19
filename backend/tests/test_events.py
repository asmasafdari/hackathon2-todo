"""Tests for CloudEvents schemas."""

import pytest
from datetime import datetime
from uuid import uuid4

from backend.events.schemas import (
    CloudEventEnvelope,
    TodoCreatedData,
    TodoUpdatedData,
    TodoCompletedData,
    TodoDeletedData,
    AgentActionExecutedData,
    AgentActionFailedData,
)
from backend.events.types import (
    SOURCE_BACKEND,
    EVENT_TODO_CREATED,
    EVENT_TODO_UPDATED,
    EVENT_TODO_COMPLETED,
    EVENT_TODO_DELETED,
    EVENT_AGENT_ACTION_EXECUTED,
    EVENT_AGENT_ACTION_FAILED,
)


class TestCloudEventEnvelope:
    """Tests for CloudEventEnvelope schema."""

    def test_create_minimal(self):
        """Test creating a minimal CloudEvent."""
        event = CloudEventEnvelope(
            source="/backend/todos",
            type="com.desktoptodo.todo.created",
            data={"test": "data"},
        )

        assert event.source == "/backend/todos"
        assert event.type == "com.desktoptodo.todo.created"
        assert event.data == {"test": "data"}
        assert event.specversion == "1.0"
        assert event.id is not None
        assert event.time is not None

    def test_create_full(self):
        """Test creating a full CloudEvent with all fields."""
        event_id = str(uuid4())
        timestamp = datetime.utcnow()

        event = CloudEventEnvelope(
            specversion="1.0",
            id=event_id,
            source="/backend/todos",
            type="com.desktoptodo.todo.created",
            time=timestamp,
            datacontenttype="application/json",
            subject="todo-123",
            data={"id": "todo-123", "title": "Test"},
        )

        assert event.id == event_id
        assert event.time == timestamp
        assert event.subject == "todo-123"

    def test_validate_source_must_start_with_slash(self):
        """Test source validation requires leading slash."""
        with pytest.raises(
            ValueError, match="source must be a URI-reference starting with /"
        ):
            CloudEventEnvelope(
                source="invalid-source",
                type="com.desktoptodo.todo.created",
                data={},
            )

    def test_validate_type_must_follow_pattern(self):
        """Test type validation requires com.desktoptodo prefix."""
        with pytest.raises(ValueError, match="type must follow pattern"):
            CloudEventEnvelope(
                source="/backend/todos",
                type="invalid.type",
                data={},
            )

    def test_to_dict(self):
        """Test conversion to dictionary."""
        event = CloudEventEnvelope(
            source="/backend/todos",
            type="com.desktoptodo.todo.created",
            data={"id": "todo-123"},
        )

        event_dict = event.to_dict()

        assert event_dict["source"] == "/backend/todos"
        assert event_dict["type"] == "com.desktoptodo.todo.created"
        assert event_dict["data"] == {"id": "todo-123"}
        assert event_dict["specversion"] == "1.0"
        assert "time" in event_dict
        assert "id" in event_dict

    def test_to_dict_with_pydantic_data(self):
        """Test to_dict with Pydantic model data."""
        todo_data = TodoCreatedData(
            id=uuid4(),
            title="Test Todo",
            description="Test Description",
            completed=False,
            created_at=datetime.utcnow(),
        )

        event = CloudEventEnvelope(
            source="/backend/todos",
            type=EVENT_TODO_CREATED,
            data=todo_data,
        )

        event_dict = event.to_dict()

        assert "data" in event_dict
        assert event_dict["data"]["title"] == "Test Todo"


class TestTodoCreatedData:
    """Tests for TodoCreatedData schema."""

    def test_create_minimal(self):
        """Test creating minimal TodoCreatedData."""
        todo_id = uuid4()
        created_at = datetime.utcnow()

        data = TodoCreatedData(
            id=todo_id,
            title="Test Todo",
            created_at=created_at,
        )

        assert data.id == todo_id
        assert data.title == "Test Todo"
        assert data.description is None
        assert data.completed is False
        assert data.created_at == created_at
        assert data.actor_id is None

    def test_create_full(self):
        """Test creating full TodoCreatedData."""
        todo_id = uuid4()
        created_at = datetime.utcnow()

        data = TodoCreatedData(
            id=todo_id,
            title="Test Todo",
            description="Test Description",
            completed=True,
            created_at=created_at,
            actor_id="user-123",
        )

        assert data.description == "Test Description"
        assert data.completed is True
        assert data.actor_id == "user-123"

    def test_title_validation_min_length(self):
        """Test title must not be empty."""
        with pytest.raises(ValueError):
            TodoCreatedData(
                id=uuid4(),
                title="",
                created_at=datetime.utcnow(),
            )

    def test_title_validation_max_length(self):
        """Test title max length validation."""
        with pytest.raises(ValueError):
            TodoCreatedData(
                id=uuid4(),
                title="x" * 256,  # Exceeds 255 char limit
                created_at=datetime.utcnow(),
            )


class TestTodoUpdatedData:
    """Tests for TodoUpdatedData schema."""

    def test_create(self):
        """Test creating TodoUpdatedData."""
        todo_id = uuid4()
        updated_at = datetime.utcnow()

        data = TodoUpdatedData(
            id=todo_id,
            changes={"title": "New Title"},
            previous={"title": "Old Title"},
            updated_at=updated_at,
            actor_id="user-123",
        )

        assert data.id == todo_id
        assert data.changes == {"title": "New Title"}
        assert data.previous == {"title": "Old Title"}
        assert data.updated_at == updated_at
        assert data.actor_id == "user-123"


class TestTodoCompletedData:
    """Tests for TodoCompletedData schema."""

    def test_create_completed(self):
        """Test creating for completed todo."""
        todo_id = uuid4()
        completed_at = datetime.utcnow()

        data = TodoCompletedData(
            id=todo_id,
            completed=True,
            completed_at=completed_at,
            actor_id="user-123",
        )

        assert data.id == todo_id
        assert data.completed is True
        assert data.completed_at == completed_at

    def test_create_uncompleted(self):
        """Test creating for uncompleted todo."""
        todo_id = uuid4()

        data = TodoCompletedData(
            id=todo_id,
            completed=False,
            completed_at=None,
            actor_id="user-123",
        )

        assert data.completed is False
        assert data.completed_at is None


class TestTodoDeletedData:
    """Tests for TodoDeletedData schema."""

    def test_create(self):
        """Test creating TodoDeletedData."""
        todo_id = uuid4()
        deleted_at = datetime.utcnow()

        data = TodoDeletedData(
            id=todo_id,
            title="Deleted Todo",
            deleted_at=deleted_at,
            actor_id="user-123",
        )

        assert data.id == todo_id
        assert data.title == "Deleted Todo"
        assert data.deleted_at == deleted_at
        assert data.actor_id == "user-123"


class TestAgentActionExecutedData:
    """Tests for AgentActionExecutedData schema."""

    def test_create(self):
        """Test creating AgentActionExecutedData."""
        action_id = uuid4()
        executed_at = datetime.utcnow()

        data = AgentActionExecutedData(
            action_id=action_id,
            agent_id="claude-agent-1",
            tool_name="create_todo",
            tool_input={"title": "Test"},
            tool_output={"id": "todo-123"},
            entity_id=uuid4(),
            executed_at=executed_at,
            duration_ms=150,
        )

        assert data.action_id == action_id
        assert data.agent_id == "claude-agent-1"
        assert data.tool_name == "create_todo"
        assert data.duration_ms == 150

    def test_default_action_id(self):
        """Test action_id defaults to new UUID."""
        data = AgentActionExecutedData(
            agent_id="claude-agent-1",
            tool_name="list_todos",
            tool_input={},
            tool_output={"todos": []},
            duration_ms=50,
        )

        assert data.action_id is not None

    def test_duration_must_be_non_negative(self):
        """Test duration_ms must be >= 0."""
        with pytest.raises(ValueError):
            AgentActionExecutedData(
                agent_id="claude-agent-1",
                tool_name="create_todo",
                tool_input={},
                tool_output={},
                duration_ms=-1,
            )


class TestAgentActionFailedData:
    """Tests for AgentActionFailedData schema."""

    def test_create(self):
        """Test creating AgentActionFailedData."""
        action_id = uuid4()
        failed_at = datetime.utcnow()

        data = AgentActionFailedData(
            action_id=action_id,
            agent_id="claude-agent-1",
            tool_name="create_todo",
            tool_input={"title": "Test"},
            error_type="ConnectionError",
            error_message="Could not connect to API",
            failed_at=failed_at,
        )

        assert data.action_id == action_id
        assert data.agent_id == "claude-agent-1"
        assert data.tool_name == "create_todo"
        assert data.error_type == "ConnectionError"
        assert data.error_message == "Could not connect to API"

    def test_default_action_id(self):
        """Test action_id defaults to new UUID."""
        data = AgentActionFailedData(
            agent_id="claude-agent-1",
            tool_name="create_todo",
            tool_input={},
            error_type="ValueError",
            error_message="Invalid input",
        )

        assert data.action_id is not None
