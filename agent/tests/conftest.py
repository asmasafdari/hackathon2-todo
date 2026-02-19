"""Pytest fixtures for agent tests."""

from datetime import datetime
from uuid import uuid4
import pytest
from unittest.mock import MagicMock, patch
import httpx


@pytest.fixture
def sample_todo():
    """Sample todo item for testing."""
    return {
        "id": str(uuid4()),
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": False,
        "created_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_todo_completed():
    """Sample completed todo item for testing."""
    return {
        "id": str(uuid4()),
        "title": "Call mom",
        "description": None,
        "completed": True,
        "created_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_todos(sample_todo, sample_todo_completed):
    """List of sample todos for testing."""
    return [sample_todo, sample_todo_completed]


@pytest.fixture
def mock_http_client(sample_todo, sample_todos):
    """Mock HTTP client for testing."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    return mock_client


@pytest.fixture
def mock_response_factory():
    """Factory for creating mock HTTP responses."""
    def create_response(status_code: int, json_data=None, text: str = ""):
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.json.return_value = json_data
        response.text = text
        return response
    return create_response
