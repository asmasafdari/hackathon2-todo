"""WebSocket endpoint for real-time task sync.

Connected clients receive task update events broadcast from Dapr pub/sub.
"""

import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

# Connected clients registry
_connections: list[WebSocket] = []


@router.websocket("/ws/tasks")
async def task_updates_ws(websocket: WebSocket):
    """WebSocket endpoint for receiving real-time task updates."""
    await websocket.accept()
    _connections.append(websocket)
    logger.info(f"WebSocket client connected. Total: {len(_connections)}")

    try:
        while True:
            # Keep connection alive; clients only receive, not send
            await websocket.receive_text()
    except WebSocketDisconnect:
        _connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(_connections)}")


async def broadcast_task_update(event_data: dict[str, Any]) -> int:
    """Broadcast a task update event to all connected WebSocket clients.

    Args:
        event_data: The CloudEvents payload to broadcast

    Returns:
        Number of clients that received the message
    """
    if not _connections:
        return 0

    sent = 0
    disconnected = []
    for ws in _connections:
        try:
            await ws.send_json(event_data)
            sent += 1
        except Exception:
            disconnected.append(ws)

    for ws in disconnected:
        _connections.remove(ws)

    if sent:
        logger.debug(f"Broadcast task update to {sent} clients")

    return sent
