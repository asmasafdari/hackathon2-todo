"""Recurring task consumer.

Consumes from the 'task-events' Dapr pub/sub topic and auto-creates
the next occurrence when a recurring task is completed.

Note: The primary recurring logic is handled synchronously in
TodoService.toggle_todo() via recurring_task_service.create_next_occurrence().
This consumer serves as a decoupled backup / event-driven alternative
for when the recurring task creation is handled asynchronously
(e.g., in a separate microservice deployment).
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def handle_task_event(event_data: dict) -> dict:
    """Process a task event from the task-events topic.

    Looks for todo.completed events on recurring tasks and logs them.
    The actual next-occurrence creation is handled by the TodoService
    synchronously for reliability.

    Args:
        event_data: CloudEvents payload

    Returns:
        Status dict
    """
    event_type = event_data.get("type", "")
    data = event_data.get("data", {})

    if event_type == "com.desktoptodo.todo.completed":
        task_id = data.get("id")
        completed = data.get("completed", False)

        if completed:
            logger.info(
                f"[RECURRING-CONSUMER] Task {task_id} completed. "
                f"If recurring, next occurrence was created by TodoService."
            )

    elif event_type == "com.desktoptodo.todo.recurring.created":
        new_id = data.get("id")
        parent_id = data.get("parent_id")
        title = data.get("title")
        rule = data.get("recurrence_rule")

        logger.info(
            f"[RECURRING-CONSUMER] New recurring task created: "
            f"id={new_id} parent={parent_id} title='{title}' rule={rule}"
        )

    return {
        "status": "processed",
        "event_type": event_type,
        "processed_at": datetime.utcnow().isoformat(),
    }
