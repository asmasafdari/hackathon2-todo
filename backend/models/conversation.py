"""Conversation model for chat sessions."""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.user import User
    from models.message import Message


class ConversationBase(SQLModel):
    """Base conversation fields."""

    title: Optional[str] = Field(default=None, max_length=255)


class Conversation(ConversationBase, table=True):
    """Conversation model for chat sessions."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationRead(ConversationBase):
    """Schema for reading a conversation (API response)."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""

    user_id: UUID


class ConversationUpdate(SQLModel):
    """Schema for updating a conversation."""

    title: Optional[str] = Field(default=None, max_length=255)


class ConversationWithMessages(ConversationRead):
    """Conversation with its messages."""

    messages: List["MessageRead"] = []
