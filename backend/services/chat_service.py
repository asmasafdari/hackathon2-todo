"""Chat service for AI processing with OpenAI Agents SDK."""

import logging
import sys
import traceback
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Add agent directory to path for imports
# In Docker: /app/agent/, locally: ../../agent/ relative to this file
_local_agent_path = Path(__file__).parent.parent.parent / "agent"
_docker_agent_path = Path("/app/agent")
agent_path = _docker_agent_path if _docker_agent_path.exists() else _local_agent_path
sys.path.insert(0, str(agent_path))

from agent import run_agent
from models import MessageRead


class ChatService:
    """Service for processing chat messages with AI."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def process_message(
        self, user_id: UUID, message: str, history: List[MessageRead]
    ) -> Tuple[str, Optional[List[dict]]]:
        """
        Process a message with the AI agent.

        Args:
            user_id: The user's ID (UUID converted to string for agent)
            message: The user's message
            history: Previous messages in the conversation

        Returns:
            Tuple of (response_text, tool_calls)
        """
        # Build context from history
        context = []
        for msg in history:
            context.append({"role": msg.role, "content": msg.content})

        # Run the agent with user_id
        try:
            logger.info(f"Running agent for user {user_id} with message: {message[:50]}")
            response_text, updated_context, tool_calls = await run_agent(
                user_input=message,
                user_id=str(user_id),
                context=context,
            )
            logger.info(f"Agent responded: {response_text[:100]}")
            return response_text, tool_calls if tool_calls else None
        except Exception as e:
            logger.error(f"Agent execution failed: {type(e).__name__}: {e}")
            logger.error(traceback.format_exc())
            raise Exception(f"Agent execution failed: {str(e)}")
