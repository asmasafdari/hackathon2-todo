"""Unit tests for MCP server tools."""

from unittest.mock import patch, MagicMock
from uuid import uuid4
import pytest
import httpx

# Import after setting up path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import (
    create_todo,
    list_todos,
    get_todo,
    update_todo,
    toggle_todo,
    delete_todo,
    TodoNotFoundError,
    TodoAPIError,
)


class TestCreateTodo:
    """Tests for create_todo tool."""

    def test_create_todo_success(self, mock_response_factory, sample_todo):
        """Test successful todo creation."""
        response = mock_response_factory(201, sample_todo)

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            result = create_todo("Buy groceries", "Milk, eggs, bread")

            assert result == sample_todo
            mock_client.post.assert_called_once()

    def test_create_todo_without_description(self, mock_response_factory, sample_todo):
        """Test todo creation without description."""
        sample_todo["description"] = None
        response = mock_response_factory(201, sample_todo)

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = response
            mock_get_client.return_value = mock_client

            result = create_todo("Buy groceries")

            assert result == sample_todo

    def test_create_todo_connection_error(self):
        """Test handling of connection errors."""
        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = httpx.ConnectError("Connection failed")
            mock_get_client.return_value = mock_client

            with pytest.raises(TodoAPIError) as exc_info:
                create_todo("Buy groceries")

            assert "trouble reaching" in str(exc_info.value)


class TestListTodos:
    """Tests for list_todos tool."""

    def test_list_todos_all(self, mock_response_factory, sample_todos):
        """Test listing all todos."""
        response = mock_response_factory(200, sample_todos)

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = response
            mock_get_client.return_value = mock_client

            result = list_todos()

            assert len(result) == 2

    def test_list_todos_pending_filter(self, mock_response_factory, sample_todos):
        """Test listing only pending todos."""
        response = mock_response_factory(200, sample_todos)

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = response
            mock_get_client.return_value = mock_client

            result = list_todos(filter="pending")

            assert len(result) == 1
            assert result[0]["completed"] is False

    def test_list_todos_completed_filter(self, mock_response_factory, sample_todos):
        """Test listing only completed todos."""
        response = mock_response_factory(200, sample_todos)

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = response
            mock_get_client.return_value = mock_client

            result = list_todos(filter="completed")

            assert len(result) == 1
            assert result[0]["completed"] is True


class TestGetTodo:
    """Tests for get_todo tool."""

    def test_get_todo_success(self, mock_response_factory, sample_todo):
        """Test getting a specific todo."""
        todo_id = sample_todo["id"]
        response = mock_response_factory(200, sample_todo)

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = response
            mock_get_client.return_value = mock_client

            result = get_todo(todo_id)

            assert result == sample_todo

    def test_get_todo_not_found(self, mock_response_factory):
        """Test 404 handling for get_todo."""
        todo_id = str(uuid4())
        response = mock_response_factory(404, text="Not found")

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = response
            mock_get_client.return_value = mock_client

            with pytest.raises(TodoNotFoundError) as exc_info:
                get_todo(todo_id)

            assert "couldn't find" in str(exc_info.value)


class TestUpdateTodo:
    """Tests for update_todo tool."""

    def test_update_todo_success(self, mock_response_factory, sample_todo):
        """Test updating a todo."""
        todo_id = sample_todo["id"]
        updated_todo = {**sample_todo, "title": "Updated title"}
        response = mock_response_factory(200, updated_todo)

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.put.return_value = response
            mock_get_client.return_value = mock_client

            result = update_todo(todo_id, title="Updated title")

            assert result["title"] == "Updated title"

    def test_update_todo_no_fields(self):
        """Test that update requires at least one field."""
        todo_id = str(uuid4())

        with pytest.raises(ValueError) as exc_info:
            update_todo(todo_id)

        assert "at least one field" in str(exc_info.value).lower()

    def test_update_todo_not_found(self, mock_response_factory):
        """Test 404 handling for update_todo."""
        todo_id = str(uuid4())
        response = mock_response_factory(404, text="Not found")

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.put.return_value = response
            mock_get_client.return_value = mock_client

            with pytest.raises(TodoNotFoundError):
                update_todo(todo_id, title="New title")


class TestToggleTodo:
    """Tests for toggle_todo tool."""

    def test_toggle_todo_success(self, mock_response_factory, sample_todo):
        """Test toggling a todo's completion status."""
        todo_id = sample_todo["id"]
        toggled_todo = {**sample_todo, "completed": True}
        response = mock_response_factory(200, toggled_todo)

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.patch.return_value = response
            mock_get_client.return_value = mock_client

            result = toggle_todo(todo_id)

            assert result["completed"] is True

    def test_toggle_todo_not_found(self, mock_response_factory):
        """Test 404 handling for toggle_todo."""
        todo_id = str(uuid4())
        response = mock_response_factory(404, text="Not found")

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.patch.return_value = response
            mock_get_client.return_value = mock_client

            with pytest.raises(TodoNotFoundError):
                toggle_todo(todo_id)


class TestDeleteTodo:
    """Tests for delete_todo tool."""

    def test_delete_todo_success(self, mock_response_factory):
        """Test deleting a todo."""
        todo_id = str(uuid4())
        response = mock_response_factory(204)

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.delete.return_value = response
            mock_get_client.return_value = mock_client

            result = delete_todo(todo_id)

            assert result["success"] is True
            assert result["deleted_id"] == todo_id

    def test_delete_todo_not_found(self, mock_response_factory):
        """Test 404 handling for delete_todo."""
        todo_id = str(uuid4())
        response = mock_response_factory(404, text="Not found")

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.delete.return_value = response
            mock_get_client.return_value = mock_client

            with pytest.raises(TodoNotFoundError):
                delete_todo(todo_id)

    def test_delete_todo_timeout(self):
        """Test timeout handling for delete_todo."""
        todo_id = str(uuid4())

        with patch("mcp_server.get_http_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.delete.side_effect = httpx.TimeoutException("Timeout")
            mock_get_client.return_value = mock_client

            with pytest.raises(TodoAPIError) as exc_info:
                delete_todo(todo_id)

            assert "took too long" in str(exc_info.value)
