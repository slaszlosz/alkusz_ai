from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import Conversation, Message
from app.core.rag import RAGPipeline
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])
rag = RAGPipeline()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    category: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    sources: List[Dict]


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a chat message and get AI response"""

    # Get or create conversation
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation
        conversation = Conversation(title=request.message[:50])
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Get conversation history
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    history_messages = result.scalars().all()

    # Format history for RAG
    conversation_history = []
    for msg in history_messages:
        conversation_history.append({
            "role": msg.role,
            "content": msg.content
        })

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)

    # Generate response using RAG
    rag_response = rag.generate_response(
        query=request.message,
        conversation_history=conversation_history,
        category=request.category
    )

    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=rag_response["answer"],
        sources=rag_response["sources"]
    )
    db.add(assistant_message)

    await db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        message=rag_response["answer"],
        sources=rag_response["sources"]
    )


@router.get("/conversations")
async def get_conversations(db: AsyncSession = Depends(get_db)):
    """Get all conversations"""
    result = await db.execute(
        select(Conversation).order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    return [
        {
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        }
        for conv in conversations
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Get conversation with all messages"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "sources": msg.sources,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }


@router.post("/stream")
async def chat_stream(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a chat message and get streaming AI response (Server-Sent Events)"""

    # Get or create conversation
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation
        conversation = Conversation(title=request.message[:50])
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Get conversation history
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    history_messages = result.scalars().all()

    # Format history for RAG
    conversation_history = []
    for msg in history_messages:
        conversation_history.append({
            "role": msg.role,
            "content": msg.content
        })

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.commit()

    # Stream response
    async def event_generator():
        # Send conversation_id first
        yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation.id})}\n\n"

        full_response = ""
        for chunk in rag.generate_response_stream(
            query=request.message,
            conversation_history=conversation_history,
            category=request.category,
            conversation_id=conversation.id
        ):
            full_response += chunk
            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"

        # After streaming completes, save assistant message and send sources
        # Note: sources are calculated in generate_response_stream but not returned
        # We need to get them separately
        rag_response = rag.generate_response(
            query=request.message,
            conversation_history=conversation_history,
            category=request.category
        )

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_response,
            sources=rag_response["sources"]
        )
        db.add(assistant_message)
        await db.commit()

        yield f"data: {json.dumps({'type': 'sources', 'sources': rag_response['sources']})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
