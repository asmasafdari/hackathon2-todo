from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import field_validator


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
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TodoCreate(TodoBase):
    """Schema for creating a new Todo."""
    pass


class TodoUpdate(SQLModel):
    """Schema for updating a Todo (all fields optional)."""
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

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
    completed: bool
    created_at: datetime
