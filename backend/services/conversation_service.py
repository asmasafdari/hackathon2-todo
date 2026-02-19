"""Conversation service for managing chat sessions."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from models import (
    Conversation,
    ConversationCreate,
    ConversationRead,
    Message,
    MessageCreate,
    MessageRead,
)


class ConversationService:
    """Service for conversation operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_conversation(self, data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(user_id=data.user_id, title=data.title)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get a conversation by ID."""
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_user_conversations(self, user_id: UUID) -> List[ConversationRead]:
        """Get all conversations for a user with message counts."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
        )
        conversations = result.scalars().all()

        # Add message counts
        conversation_reads = []
        for conv in conversations:
            count_result = await self.session.execute(
                select(func.count(Message.id)).where(Message.conversation_id == conv.id)
            )
            message_count = count_result.scalar()

            conversation_reads.append(
                ConversationRead(
                    id=conv.id,
                    user_id=conv.user_id,
                    title=conv.title,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=message_count,
                )
            )

        return conversation_reads

    async def add_message(self, data: MessageCreate) -> Message:
        """Add a message to a conversation."""
        import json

        message = Message(
            conversation_id=data.conversation_id,
            user_id=data.user_id,
            role=data.role,
            content=data.content,
            tool_calls=json.dumps(data.tool_calls) if data.tool_calls else None,
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_conversation_messages(
        self, conversation_id: UUID, limit: int = 50
    ) -> List[MessageRead]:
        """Get messages for a conversation."""
        import json

        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
        )
        messages = result.scalars().all()

        # Parse tool_calls JSON
        message_reads = []
        for msg in messages:
            tool_calls = None
            if msg.tool_calls:
                try:
                    tool_calls = json.loads(msg.tool_calls)
                except json.JSONDecodeError:
                    pass

            message_reads.append(
                MessageRead(
                    id=msg.id,
                    conversation_id=msg.conversation_id,
                    user_id=msg.user_id,
                    role=msg.role,
                    content=msg.content,
                    tool_calls=tool_calls,
                    created_at=msg.created_at,
                )
            )

        return message_reads
