"""Message model for chat history."""

from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator

if TYPE_CHECKING:
    from models.user import User
    from models.conversation import Conversation


class MessageBase(SQLModel):
    """Base message fields."""

    role: str = Field(max_length=50)  # 'user' or 'assistant'
    content: str = Field()


class Message(MessageBase, table=True):
    """Message model for chat history."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    tool_calls: Optional[str] = Field(default=None)  # JSON string of tool calls
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(
        back_populates="messages",
        sa_relationship_kwargs={"foreign_keys": "[Message.conversation_id]"},
    )
    user: Optional["User"] = Relationship(
        back_populates="messages",
        sa_relationship_kwargs={"foreign_keys": "[Message.user_id]"},
    )

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ["user", "assistant", "system"]:
            raise ValueError("Role must be 'user', 'assistant', or 'system'")
        return v


class MessageCreate(SQLModel):
    """Schema for creating a new message."""

    conversation_id: UUID
    user_id: UUID
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


class MessageUpdate(SQLModel):
    """Schema for updating a message."""

    content: Optional[str] = None


class MessageRead(MessageBase):
    """Schema for reading a message (API response)."""

    id: UUID
    conversation_id: UUID
    user_id: UUID
    tool_calls: Optional[List[Dict[str, Any]]] = None
    created_at: datetime


class ToolCall(SQLModel):
    """Schema for a single tool call."""

    tool: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None


class MessageWithToolCalls(MessageRead):
    """Message with parsed tool calls."""

    parsed_tool_calls: List[ToolCall] = []
