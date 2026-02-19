"""User model for multi-user support with Clerk authentication."""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr

if TYPE_CHECKING:
    from models.conversation import Conversation
    from models.message import Message
    from models.todo import Todo


class UserBase(SQLModel):
    """Base user fields."""

    email: EmailStr = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """User model with Clerk authentication."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str = Field(default="clerk-managed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")
    todos: List["Todo"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    pass


class UserUpdate(SQLModel):
    """Schema for updating a user."""

    name: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """Schema for reading a user (API response)."""

    id: UUID
    created_at: datetime
    updated_at: datetime


class UserWithStats(UserRead):
    """User with conversation and task statistics."""

    conversation_count: int = 0
    todo_count: int = 0
    completed_todo_count: int = 0
