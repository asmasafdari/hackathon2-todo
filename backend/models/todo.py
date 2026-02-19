"""Todo model for task management."""

import enum
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Enum as SAEnum, JSON
from pydantic import field_validator

if TYPE_CHECKING:
    from models.user import User


class Priority(str, enum.Enum):
    """Task priority levels."""
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TodoBase(SQLModel):
    """Shared fields for Todo (used in create/update)."""

    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if v is None:
            raise ValueError("Title is required")
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return None


class Todo(TodoBase, table=True):
    """Database model for Todo."""

    __tablename__ = "todos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id", index=True)
    completed: bool = Field(default=False)
    priority: Optional[Priority] = Field(
        default=None,
        sa_column=Column(SAEnum(Priority, name="priority_enum", create_constraint=False), nullable=True),
    )
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    due_date: Optional[datetime] = Field(default=None)
    remind_at: Optional[datetime] = Field(default=None)
    recurrence_rule: Optional[str] = Field(default=None, max_length=50)
    recurrence_parent_id: Optional[UUID] = Field(default=None, foreign_key="todos.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="todos")


class TodoCreate(TodoBase):
    """Schema for creating a new Todo."""

    user_id: Optional[UUID] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence_rule: Optional[str] = None


class TodoUpdate(SQLModel):
    """Schema for updating a Todo (all fields optional)."""

    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence_rule: Optional[str] = None

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty")
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return None


class TodoRead(TodoBase):
    """Schema for reading a Todo (API response)."""

    id: UUID
    user_id: Optional[UUID]
    completed: bool
    priority: Optional[Priority]
    tags: Optional[List[str]]
    due_date: Optional[datetime]
    remind_at: Optional[datetime]
    recurrence_rule: Optional[str]
    recurrence_parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
