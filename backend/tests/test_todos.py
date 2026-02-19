"""Tests for the todos API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestCreateTodo:
    """Tests for POST /api/todos endpoint."""

    async def test_create_todo_success(self, client: AsyncClient):
        """Test creating a todo with valid data."""
        response = await client.post(
            "/api/todos",
            json={"title": "Buy groceries", "description": "Milk, eggs, and bread"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, and bread"
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data

    async def test_create_todo_without_description(self, client: AsyncClient):
        """Test creating a todo without description."""
        response = await client.post("/api/todos", json={"title": "Simple task"})

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Simple task"
        assert data["description"] is None

    async def test_create_todo_empty_title(self, client: AsyncClient):
        """Test creating a todo with empty title fails."""
        response = await client.post(
            "/api/todos", json={"title": "", "description": "Description"}
        )

        assert response.status_code == 422

    async def test_create_todo_missing_title(self, client: AsyncClient):
        """Test creating a todo without title fails."""
        response = await client.post(
            "/api/todos", json={"description": "Description only"}
        )

        assert response.status_code == 422


class TestListTodos:
    """Tests for GET /api/todos endpoint."""

    async def test_list_todos_empty(self, client: AsyncClient):
        """Test listing todos when none exist."""
        response = await client.get("/api/todos")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_list_todos_with_items(self, client: AsyncClient, sample_todo):
        """Test listing todos returns created items."""
        response = await client.get("/api/todos")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == sample_todo["title"]

    async def test_list_todos_ordering(self, client: AsyncClient):
        """Test todos are returned in creation order."""
        # Create multiple todos
        await client.post("/api/todos", json={"title": "First"})
        await client.post("/api/todos", json={"title": "Second"})
        await client.post("/api/todos", json={"title": "Third"})

        response = await client.get("/api/todos")
        data = response.json()

        assert len(data) == 3
        assert data[0]["title"] == "First"
        assert data[1]["title"] == "Second"
        assert data[2]["title"] == "Third"


class TestGetTodo:
    """Tests for GET /api/todos/{id} endpoint."""

    async def test_get_todo_success(self, client: AsyncClient, sample_todo):
        """Test getting a specific todo."""
        todo_id = sample_todo["id"]
        response = await client.get(f"/api/todos/{todo_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == sample_todo["title"]

    async def test_get_todo_not_found(self, client: AsyncClient):
        """Test getting a non-existent todo returns 404."""
        response = await client.get("/api/todos/123e4567-e89b-12d3-a456-426614174000")

        assert response.status_code == 404
        assert "detail" in response.json()

    async def test_get_todo_invalid_id(self, client: AsyncClient):
        """Test getting a todo with invalid ID format."""
        response = await client.get("/api/todos/invalid-id")

        assert response.status_code == 422


class TestUpdateTodo:
    """Tests for PUT /api/todos/{id} endpoint."""

    async def test_update_todo_title(self, client: AsyncClient, sample_todo):
        """Test updating a todo's title."""
        todo_id = sample_todo["id"]
        response = await client.put(
            f"/api/todos/{todo_id}", json={"title": "Updated Title"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == sample_todo["description"]

    async def test_update_todo_description(self, client: AsyncClient, sample_todo):
        """Test updating a todo's description."""
        todo_id = sample_todo["id"]
        response = await client.put(
            f"/api/todos/{todo_id}", json={"description": "Updated Description"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated Description"
        assert data["title"] == sample_todo["title"]

    async def test_update_todo_both_fields(self, client: AsyncClient, sample_todo):
        """Test updating both title and description."""
        todo_id = sample_todo["id"]
        response = await client.put(
            f"/api/todos/{todo_id}",
            json={"title": "New Title", "description": "New Description"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "New Description"

    async def test_update_todo_not_found(self, client: AsyncClient):
        """Test updating a non-existent todo returns 404."""
        response = await client.put(
            "/api/todos/123e4567-e89b-12d3-a456-426614174000",
            json={"title": "New Title"},
        )

        assert response.status_code == 404

    async def test_update_todo_no_fields(self, client: AsyncClient, sample_todo):
        """Test updating without any fields fails."""
        todo_id = sample_todo["id"]
        response = await client.put(f"/api/todos/{todo_id}", json={})

        # Should either fail validation or return unchanged todo
        assert response.status_code in [200, 422]


class TestToggleTodo:
    """Tests for PATCH /api/todos/{id}/toggle endpoint."""

    async def test_toggle_todo_to_completed(self, client: AsyncClient, sample_todo):
        """Test toggling an incomplete todo to completed."""
        todo_id = sample_todo["id"]
        assert sample_todo["completed"] is False

        response = await client.patch(f"/api/todos/{todo_id}/toggle")

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    async def test_toggle_todo_to_incomplete(self, client: AsyncClient, sample_todo):
        """Test toggling a completed todo back to incomplete."""
        todo_id = sample_todo["id"]

        # First toggle to completed
        await client.patch(f"/api/todos/{todo_id}/toggle")

        # Toggle back to incomplete
        response = await client.patch(f"/api/todos/{todo_id}/toggle")

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is False

    async def test_toggle_todo_not_found(self, client: AsyncClient):
        """Test toggling a non-existent todo returns 404."""
        response = await client.patch(
            "/api/todos/123e4567-e89b-12d3-a456-426614174000/toggle"
        )

        assert response.status_code == 404


class TestDeleteTodo:
    """Tests for DELETE /api/todos/{id} endpoint."""

    async def test_delete_todo_success(self, client: AsyncClient, sample_todo):
        """Test deleting a todo."""
        todo_id = sample_todo["id"]

        response = await client.delete(f"/api/todos/{todo_id}")

        assert response.status_code == 204

        # Verify it's gone
        get_response = await client.get(f"/api/todos/{todo_id}")
        assert get_response.status_code == 404

    async def test_delete_todo_not_found(self, client: AsyncClient):
        """Test deleting a non-existent todo returns 404."""
        response = await client.delete(
            "/api/todos/123e4567-e89b-12d3-a456-426614174000"
        )

        assert response.status_code == 404

    async def test_delete_todo_invalid_id(self, client: AsyncClient):
        """Test deleting with invalid ID format."""
        response = await client.delete("/api/todos/invalid-id")

        assert response.status_code == 422


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    async def test_health_check(self, client: AsyncClient):
        """Test health endpoint returns healthy status."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "backend"
