"""Service for handling recurring task logic.

When a recurring task is completed, this service creates the next
occurrence based on the recurrence_rule.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models import Todo, TodoCreate

logger = logging.getLogger(__name__)

RECURRENCE_DELTAS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "monthly": timedelta(days=30),  # Approximate; good enough for MVP
}


async def create_next_occurrence(
    session: AsyncSession,
    completed_todo: Todo,
) -> Optional[Todo]:
    """Create the next occurrence of a recurring task after completion.

    Args:
        session: Database session
        completed_todo: The todo that was just completed

    Returns:
        The newly created todo, or None if not recurring
    """
    if not completed_todo.recurrence_rule:
        return None

    rule = completed_todo.recurrence_rule.lower()
    delta = RECURRENCE_DELTAS.get(rule)
    if not delta:
        logger.warning(f"Unknown recurrence rule '{rule}' for todo {completed_todo.id}")
        return None

    # Calculate next due date
    base_date = completed_todo.due_date or datetime.utcnow()
    next_due = base_date + delta

    # Calculate next reminder (same offset from due_date if set)
    next_remind = None
    if completed_todo.remind_at and completed_todo.due_date:
        remind_offset = completed_todo.due_date - completed_todo.remind_at
        next_remind = next_due - remind_offset

    new_todo = Todo(
        title=completed_todo.title,
        description=completed_todo.description,
        user_id=completed_todo.user_id,
        priority=completed_todo.priority,
        tags=completed_todo.tags,
        due_date=next_due,
        remind_at=next_remind,
        recurrence_rule=completed_todo.recurrence_rule,
        recurrence_parent_id=completed_todo.id,
        completed=False,
    )

    session.add(new_todo)
    await session.commit()
    await session.refresh(new_todo)

    logger.info(
        f"Created next occurrence {new_todo.id} for recurring task {completed_todo.id} "
        f"(rule={rule}, next_due={next_due})"
    )

    return new_todo
