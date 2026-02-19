"""MCP Server with todo management tools using FastMCP.

Tools:
- add_task: Create a new task
- list_tasks: Retrieve tasks from the list
- complete_task: Mark a task as complete
- delete_task: Remove a task from the list
- update_task: Modify task title or description
- set_priority: Set task priority level
- add_tags: Add tags to a task
- remove_tag: Remove a tag from a task
- search_tasks: Search tasks by keyword
- set_due_date: Set a due date on a task
- set_reminder: Set a reminder time on a task
- list_overdue: List overdue tasks
- set_recurring: Make a task recurring
- cancel_recurring: Cancel recurrence on a task
"""

from typing import Optional
from uuid import UUID as _UUID
import httpx
from mcp.server.fastmcp import FastMCP

from config import get_settings


# Custom exceptions for user-friendly error messages
class TodoNotFoundError(Exception):
    """Raised when a todo is not found."""

    pass


class TodoAPIError(Exception):
    """Raised when the API returns an error."""

    pass


# Initialize FastMCP server
mcp = FastMCP("todo-assistant")
settings = get_settings()


def get_http_client() -> httpx.Client:
    """Create HTTP client with configured timeout."""
    return httpx.Client(timeout=settings.request_timeout)


def handle_response_error(
    response: httpx.Response, todo_id: Optional[str] = None
) -> None:
    """Handle HTTP error responses with user-friendly messages."""
    if response.status_code == 404:
        raise TodoNotFoundError(
            f"I couldn't find that task{f' (ID: {todo_id})' if todo_id else ''}."
        )
    elif response.status_code >= 400:
        raise TodoAPIError(f"API error: {response.status_code} - {response.text}")


def _is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        _UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def _resolve_task_id(client: httpx.Client, user_id: str, task_id: str) -> str:
    """Resolve a task_id that may be a name/title into an actual UUID.

    If task_id is already a valid UUID, return it as-is.
    Otherwise, list the user's tasks and find a match by title.
    """
    if _is_valid_uuid(task_id):
        return task_id

    # task_id is a name or index — fetch tasks to resolve
    response = client.get(f"{settings.api_todos_url}?user_id={user_id}")
    handle_response_error(response)
    tasks = response.json()

    if not tasks:
        raise TodoNotFoundError("You don't have any tasks.")

    # If task_id is a numeric index (e.g. "1", "2"), treat as 1-based list index
    stripped = task_id.strip()
    if stripped.isdigit():
        index = int(stripped) - 1  # convert to 0-based
        if 0 <= index < len(tasks):
            return str(tasks[index]["id"])
        raise TodoNotFoundError(
            f"Task number {stripped} is out of range. You have {len(tasks)} task(s)."
        )

    # Try exact match first (case-insensitive), then partial match
    search = stripped.lower()
    exact = [t for t in tasks if t.get("title", "").lower().strip() == search]
    if len(exact) == 1:
        return str(exact[0]["id"])

    partial = [t for t in tasks if search in t.get("title", "").lower()]
    if len(partial) == 1:
        return str(partial[0]["id"])
    if len(partial) > 1:
        names = ", ".join(f"'{t.get('title', '')}'" for t in partial[:5])
        raise TodoAPIError(
            f"I found {len(partial)} tasks matching '{task_id}': {names}. "
            "Please be more specific."
        )

    raise TodoNotFoundError(f"I couldn't find a task matching '{task_id}'.")


@mcp.tool()
def add_task(user_id: str, title: str, description: Optional[str] = None, priority: Optional[str] = None, tags: Optional[str] = None, due_date: Optional[str] = None, recurrence_rule: Optional[str] = None) -> dict:
    """
    Create a new task.

    Args:
        user_id: The user's identifier (required)
        title: The title of the task (required, max 255 chars)
        description: Optional detailed description (max 1000 chars)
        priority: Optional priority level (low, medium, high, urgent)
        tags: Optional comma-separated tags (e.g., "work,urgent")
        due_date: Optional due date in ISO format (e.g., "2026-02-20T09:00:00")
        recurrence_rule: Optional recurrence rule (daily, weekly, monthly)

    Returns:
        Dict with task_id, status, title
    """
    try:
        with get_http_client() as client:
            payload = {"title": title, "user_id": user_id}
            if description:
                payload["description"] = description
            if priority:
                payload["priority"] = priority
            if tags:
                payload["tags"] = [t.strip() for t in tags.split(",")]
            if due_date:
                payload["due_date"] = due_date
            if recurrence_rule:
                payload["recurrence_rule"] = recurrence_rule

            response = client.post(settings.api_todos_url, json=payload)
            handle_response_error(response)
            result = response.json()

            return {
                "task_id": str(result.get("id", "")),
                "status": "created",
                "title": result.get("title", title),
            }
    except httpx.ConnectError:
        raise TodoAPIError(
            "I'm having trouble reaching the todo service. Is it running?"
        )
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def list_tasks(user_id: str, status: str = "all", priority: Optional[str] = None, tag: Optional[str] = None, sort_by: Optional[str] = None) -> list:
    """
    Retrieve tasks from the list with optional filtering.

    Args:
        user_id: The user's identifier (required)
        status: Filter by status - 'all' (default), 'pending', or 'completed'
        priority: Filter by priority level (low, medium, high, urgent)
        tag: Filter by tag name
        sort_by: Sort order - 'created_at' (default), 'priority', or 'due_date'

    Returns:
        Array of task objects
    """
    try:
        with get_http_client() as client:
            params = {"user_id": user_id}
            if status and status != "all":
                params["status"] = status
            if priority:
                params["priority"] = priority
            if tag:
                params["tag"] = tag
            if sort_by:
                params["sort_by"] = sort_by

            response = client.get(settings.api_todos_url, params=params)
            handle_response_error(response)
            return response.json()
    except httpx.ConnectError:
        raise TodoAPIError(
            "I'm having trouble reaching the todo service. Is it running?"
        )
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def complete_task(user_id: str, task_id: str) -> dict:
    """
    Mark a task as complete.

    Args:
        user_id: The user's identifier (required)
        task_id: The ID of the task to complete (required)

    Returns:
        Dict with task_id, status, title
    """
    try:
        with get_http_client() as client:
            resolved_id = _resolve_task_id(client, user_id, task_id)
            response = client.patch(f"{settings.api_todos_url}/{resolved_id}/toggle")
            handle_response_error(response, resolved_id)
            result = response.json()

            return {
                "task_id": str(result.get("id", resolved_id)),
                "status": "completed",
                "title": result.get("title", ""),
            }
    except httpx.ConnectError:
        raise TodoAPIError(
            "I'm having trouble reaching the todo service. Is it running?"
        )
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def delete_task(user_id: str, task_id: str) -> dict:
    """
    Remove a task from the list.

    Args:
        user_id: The user's identifier (required)
        task_id: The ID of the task to delete (required)

    Returns:
        Dict with task_id, status, title
    """
    try:
        with get_http_client() as client:
            resolved_id = _resolve_task_id(client, user_id, task_id)

            get_response = client.get(f"{settings.api_todos_url}/{resolved_id}")
            if get_response.status_code == 404:
                raise TodoNotFoundError("I couldn't find that task.")

            task_data = get_response.json()
            title = task_data.get("title", "")

            response = client.delete(f"{settings.api_todos_url}/{resolved_id}")
            if response.status_code == 404:
                raise TodoNotFoundError("I couldn't find that task.")
            handle_response_error(response, resolved_id)

            return {
                "task_id": str(resolved_id),
                "status": "deleted",
                "title": title,
            }
    except httpx.ConnectError:
        raise TodoAPIError(
            "I'm having trouble reaching the todo service. Is it running?"
        )
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Modify task title or description.

    Args:
        user_id: The user's identifier (required)
        task_id: The ID of the task to update (required)
        title: New title (optional, max 255 chars)
        description: New description (optional, max 1000 chars)

    Returns:
        Dict with task_id, status, title
    """
    if title is None and description is None:
        raise ValueError(
            "At least one field (title or description) must be provided to update."
        )

    try:
        with get_http_client() as client:
            resolved_id = _resolve_task_id(client, user_id, task_id)

            payload = {}
            if title is not None:
                payload["title"] = title
            if description is not None:
                payload["description"] = description

            response = client.put(f"{settings.api_todos_url}/{resolved_id}", json=payload)
            handle_response_error(response, resolved_id)
            result = response.json()

            return {
                "task_id": str(result.get("id", resolved_id)),
                "status": "updated",
                "title": result.get("title", title or ""),
            }
    except httpx.ConnectError:
        raise TodoAPIError(
            "I'm having trouble reaching the todo service. Is it running?"
        )
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def set_priority(user_id: str, task_id: str, priority: str) -> dict:
    """
    Set the priority level of a task.

    Args:
        user_id: The user's identifier (required)
        task_id: The ID or name of the task (required)
        priority: Priority level - 'low', 'medium', 'high', or 'urgent' (required)

    Returns:
        Dict with task_id, status, title, priority
    """
    valid = {"low", "medium", "high", "urgent"}
    if priority.lower() not in valid:
        raise ValueError(f"Priority must be one of: {', '.join(valid)}")

    try:
        with get_http_client() as client:
            resolved_id = _resolve_task_id(client, user_id, task_id)
            response = client.put(
                f"{settings.api_todos_url}/{resolved_id}",
                json={"priority": priority.lower()},
            )
            handle_response_error(response, resolved_id)
            result = response.json()

            return {
                "task_id": str(result.get("id", resolved_id)),
                "status": "updated",
                "title": result.get("title", ""),
                "priority": result.get("priority", priority.lower()),
            }
    except httpx.ConnectError:
        raise TodoAPIError("I'm having trouble reaching the todo service. Is it running?")
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def add_tags(user_id: str, task_id: str, tags: str) -> dict:
    """
    Add one or more tags to a task.

    Args:
        user_id: The user's identifier (required)
        task_id: The ID or name of the task (required)
        tags: Comma-separated tag names to add (e.g., "work,urgent")

    Returns:
        Dict with task_id, status, title, tags
    """
    new_tags = [t.strip() for t in tags.split(",") if t.strip()]
    if not new_tags:
        raise ValueError("At least one tag must be provided.")

    try:
        with get_http_client() as client:
            resolved_id = _resolve_task_id(client, user_id, task_id)

            # Get current task to merge tags
            get_resp = client.get(f"{settings.api_todos_url}/{resolved_id}")
            handle_response_error(get_resp, resolved_id)
            current = get_resp.json()
            existing_tags = current.get("tags") or []

            # Merge without duplicates (case-insensitive)
            existing_lower = {t.lower() for t in existing_tags}
            merged = existing_tags + [t for t in new_tags if t.lower() not in existing_lower]

            response = client.put(
                f"{settings.api_todos_url}/{resolved_id}",
                json={"tags": merged},
            )
            handle_response_error(response, resolved_id)
            result = response.json()

            return {
                "task_id": str(result.get("id", resolved_id)),
                "status": "updated",
                "title": result.get("title", ""),
                "tags": result.get("tags", merged),
            }
    except httpx.ConnectError:
        raise TodoAPIError("I'm having trouble reaching the todo service. Is it running?")
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def remove_tag(user_id: str, task_id: str, tag: str) -> dict:
    """
    Remove a tag from a task.

    Args:
        user_id: The user's identifier (required)
        task_id: The ID or name of the task (required)
        tag: The tag name to remove (required)

    Returns:
        Dict with task_id, status, title, tags
    """
    try:
        with get_http_client() as client:
            resolved_id = _resolve_task_id(client, user_id, task_id)

            # Get current task
            get_resp = client.get(f"{settings.api_todos_url}/{resolved_id}")
            handle_response_error(get_resp, resolved_id)
            current = get_resp.json()
            existing_tags = current.get("tags") or []

            # Remove tag (case-insensitive)
            updated_tags = [t for t in existing_tags if t.lower() != tag.lower()]

            response = client.put(
                f"{settings.api_todos_url}/{resolved_id}",
                json={"tags": updated_tags},
            )
            handle_response_error(response, resolved_id)
            result = response.json()

            return {
                "task_id": str(result.get("id", resolved_id)),
                "status": "updated",
                "title": result.get("title", ""),
                "tags": result.get("tags", updated_tags),
            }
    except httpx.ConnectError:
        raise TodoAPIError("I'm having trouble reaching the todo service. Is it running?")
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def search_tasks(user_id: str, query: str) -> list:
    """
    Search tasks by keyword in title or description.

    Args:
        user_id: The user's identifier (required)
        query: Search keyword (required)

    Returns:
        Array of matching task objects
    """
    try:
        with get_http_client() as client:
            response = client.get(
                settings.api_todos_url,
                params={"user_id": user_id, "search": query},
            )
            handle_response_error(response)
            return response.json()
    except httpx.ConnectError:
        raise TodoAPIError("I'm having trouble reaching the todo service. Is it running?")
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def set_due_date(user_id: str, task_id: str, due_date: str) -> dict:
    """
    Set a due date on a task.

    Args:
        user_id: The user's identifier (required)
        task_id: The ID or name of the task (required)
        due_date: Due date in ISO format (e.g., "2026-02-20T09:00:00")

    Returns:
        Dict with task_id, status, title, due_date
    """
    try:
        with get_http_client() as client:
            resolved_id = _resolve_task_id(client, user_id, task_id)
            response = client.put(
                f"{settings.api_todos_url}/{resolved_id}",
                json={"due_date": due_date},
            )
            handle_response_error(response, resolved_id)
            result = response.json()

            return {
                "task_id": str(result.get("id", resolved_id)),
                "status": "updated",
                "title": result.get("title", ""),
                "due_date": result.get("due_date"),
            }
    except httpx.ConnectError:
        raise TodoAPIError("I'm having trouble reaching the todo service. Is it running?")
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def set_reminder(user_id: str, task_id: str, remind_at: str) -> dict:
    """
    Set a reminder time on a task.

    Args:
        user_id: The user's identifier (required)
        task_id: The ID or name of the task (required)
        remind_at: Reminder time in ISO format (e.g., "2026-02-20T09:00:00")

    Returns:
        Dict with task_id, status, title, remind_at
    """
    try:
        with get_http_client() as client:
            resolved_id = _resolve_task_id(client, user_id, task_id)
            response = client.put(
                f"{settings.api_todos_url}/{resolved_id}",
                json={"remind_at": remind_at},
            )
            handle_response_error(response, resolved_id)
            result = response.json()

            return {
                "task_id": str(result.get("id", resolved_id)),
                "status": "updated",
                "title": result.get("title", ""),
                "remind_at": result.get("remind_at"),
            }
    except httpx.ConnectError:
        raise TodoAPIError("I'm having trouble reaching the todo service. Is it running?")
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def list_overdue(user_id: str) -> list:
    """
    List all overdue tasks (past due date, not completed).

    Args:
        user_id: The user's identifier (required)

    Returns:
        Array of overdue task objects
    """
    try:
        with get_http_client() as client:
            response = client.get(
                settings.api_todos_url,
                params={"user_id": user_id, "overdue": "true"},
            )
            handle_response_error(response)
            return response.json()
    except httpx.ConnectError:
        raise TodoAPIError("I'm having trouble reaching the todo service. Is it running?")
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def set_recurring(user_id: str, task_id: str, recurrence_rule: str) -> dict:
    """
    Make a task recurring. When completed, a new task will be auto-created.

    Args:
        user_id: The user's identifier (required)
        task_id: The ID or name of the task (required)
        recurrence_rule: Recurrence pattern - 'daily', 'weekly', or 'monthly' (required)

    Returns:
        Dict with task_id, status, title, recurrence_rule
    """
    valid = {"daily", "weekly", "monthly"}
    if recurrence_rule.lower() not in valid:
        raise ValueError(f"Recurrence rule must be one of: {', '.join(valid)}")

    try:
        with get_http_client() as client:
            resolved_id = _resolve_task_id(client, user_id, task_id)
            response = client.put(
                f"{settings.api_todos_url}/{resolved_id}",
                json={"recurrence_rule": recurrence_rule.lower()},
            )
            handle_response_error(response, resolved_id)
            result = response.json()

            return {
                "task_id": str(result.get("id", resolved_id)),
                "status": "updated",
                "title": result.get("title", ""),
                "recurrence_rule": result.get("recurrence_rule", recurrence_rule.lower()),
            }
    except httpx.ConnectError:
        raise TodoAPIError("I'm having trouble reaching the todo service. Is it running?")
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


@mcp.tool()
def cancel_recurring(user_id: str, task_id: str) -> dict:
    """
    Cancel recurrence on a task (task remains but stops recurring).

    Args:
        user_id: The user's identifier (required)
        task_id: The ID or name of the task (required)

    Returns:
        Dict with task_id, status, title
    """
    try:
        with get_http_client() as client:
            resolved_id = _resolve_task_id(client, user_id, task_id)

            # We need to pass a sentinel to clear the field
            # The API will accept null/empty to clear
            response = client.put(
                f"{settings.api_todos_url}/{resolved_id}",
                json={"recurrence_rule": ""},
            )
            handle_response_error(response, resolved_id)
            result = response.json()

            return {
                "task_id": str(result.get("id", resolved_id)),
                "status": "updated",
                "title": result.get("title", ""),
                "recurrence_rule": None,
            }
    except httpx.ConnectError:
        raise TodoAPIError("I'm having trouble reaching the todo service. Is it running?")
    except httpx.TimeoutException:
        raise TodoAPIError("The request took too long. Please try again.")


if __name__ == "__main__":
    # Run the MCP server via stdio
    mcp.run()
