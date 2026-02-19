"""Chat router for AI-powered todo management with Clerk auth."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import (
    User,
    Conversation,
    ConversationCreate,
    ConversationRead,
    Message,
    MessageCreate,
    MessageRead,
    TodoRead,
)
from models.user import User
from services.conversation_service import ConversationService
from services.chat_service import ChatService
from dependencies.auth import get_or_create_user

router = APIRouter(prefix="/api", tags=["Chat"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    conversation_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    conversation_id: str
    response: str
    tool_calls: Optional[list] = None


def get_conversation_service(
    session: AsyncSession = Depends(get_session),
) -> ConversationService:
    """Dependency to get ConversationService instance."""
    return ConversationService(session)


def get_chat_service(session: AsyncSession = Depends(get_session)) -> ChatService:
    """Dependency to get ChatService instance."""
    return ChatService(session)


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_or_create_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Process a chat message and return AI response.

    The user_id path param is kept for backward compatibility.
    Auth is enforced via Clerk JWT token.
    """
    # Use authenticated user's ID
    effective_user_id = current_user.id

    # Get or create conversation
    if request.conversation_id:
        try:
            conv_uuid = UUID(request.conversation_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid conversation ID")
        conversation = await conversation_service.get_conversation(conv_uuid)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation.user_id != effective_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        conversation = await conversation_service.create_conversation(
            ConversationCreate(user_id=effective_user_id)
        )

    # Store user message
    await conversation_service.add_message(
        MessageCreate(
            conversation_id=conversation.id,
            user_id=effective_user_id,
            role="user",
            content=request.message,
        )
    )

    # Get conversation history for context
    history = await conversation_service.get_conversation_messages(
        conversation.id, limit=20
    )

    # Process with AI agent
    try:
        response_text, tool_calls = await chat_service.process_message(
            user_id=effective_user_id, message=request.message, history=history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

    # Store assistant response
    await conversation_service.add_message(
        MessageCreate(
            conversation_id=conversation.id,
            user_id=effective_user_id,
            role="assistant",
            content=response_text,
            tool_calls=tool_calls,
        )
    )

    return ChatResponse(
        conversation_id=str(conversation.id), response=response_text, tool_calls=tool_calls
    )


@router.get("/{user_id}/conversations", response_model=list[ConversationRead])
async def list_conversations(
    user_id: str,
    current_user: User = Depends(get_or_create_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """List all conversations for the authenticated user."""
    return await conversation_service.get_user_conversations(current_user.id)


@router.get(
    "/{user_id}/conversations/{conversation_id}/messages",
    response_model=list[MessageRead],
)
async def get_conversation_messages(
    user_id: str,
    conversation_id: str,
    current_user: User = Depends(get_or_create_user),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Get all messages in a conversation."""
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    conversation = await conversation_service.get_conversation(conv_uuid)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return await conversation_service.get_conversation_messages(conv_uuid)
