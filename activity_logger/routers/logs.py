"""Router for activity log queries."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from activity_logger.database import get_session
from activity_logger.models import ActivityLog, ActivityLogRead, ActivityStats

router = APIRouter(prefix="/logs", tags=["activity-logs"])


@router.get("", response_model=list[ActivityLogRead])
async def list_logs(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    todo_id: Optional[str] = Query(None, description="Filter by todo ID"),
    start_date: Optional[datetime] = Query(
        None, description="Filter from date (ISO format)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filter to date (ISO format)"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    session: AsyncSession = Depends(get_session),
):
    """
    Query activity logs with optional filtering.

    Returns a list of activity log entries sorted by timestamp (newest first).
    """
    query = select(ActivityLog)

    # Apply filters
    if event_type:
        query = query.where(ActivityLog.event_type == event_type)

    if todo_id:
        query = query.where(ActivityLog.todo_id == todo_id)

    if start_date:
        query = query.where(ActivityLog.timestamp >= start_date)

    if end_date:
        query = query.where(ActivityLog.timestamp <= end_date)

    # Order by timestamp descending (newest first)
    query = query.order_by(ActivityLog.timestamp.desc())

    # Apply pagination
    query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    logs = result.scalars().all()

    return logs


@router.get("/stats", response_model=ActivityStats)
async def get_stats(
    start_date: Optional[datetime] = Query(None, description="From date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="To date (ISO format)"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get statistics about activity logs.

    Returns total count, breakdown by event type, and date range.
    """
    # Base query for filtering
    base_query = select(ActivityLog)
    if start_date:
        base_query = base_query.where(ActivityLog.timestamp >= start_date)
    if end_date:
        base_query = base_query.where(ActivityLog.timestamp <= end_date)

    # Get total count
    count_query = select(func.count(ActivityLog.id)).select_from(base_query.subquery())
    total_result = await session.execute(count_query)
    total_events = total_result.scalar()

    # Get count by event type
    type_count_query = (
        select(ActivityLog.event_type, func.count(ActivityLog.id))
        .select_from(base_query.subquery())
        .group_by(ActivityLog.event_type)
    )
    type_count_result = await session.execute(type_count_query)
    events_by_type = {row[0]: row[1] for row in type_count_result.all()}

    # Get date range
    min_date_query = select(func.min(ActivityLog.timestamp)).select_from(
        base_query.subquery()
    )
    max_date_query = select(func.max(ActivityLog.timestamp)).select_from(
        base_query.subquery()
    )

    min_date_result = await session.execute(min_date_query)
    max_date_result = await session.execute(max_date_query)

    min_date = min_date_result.scalar()
    max_date = max_date_result.scalar()

    return ActivityStats(
        total_events=total_events,
        events_by_type=events_by_type,
        date_range={"start": min_date, "end": max_date},
    )


@router.get("/{log_id}", response_model=ActivityLogRead)
async def get_log(log_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Get a specific activity log entry by ID.
    """
    result = await session.execute(select(ActivityLog).where(ActivityLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    return log
