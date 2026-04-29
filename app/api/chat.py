"""
Chat API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import uuid

from app.db.database import get_db
from app.db.models import Chat, Message, Workspace
from app.services.chat_service import ChatService

router = APIRouter()


class MessageCreate(BaseModel):
    role: str
    content: str
    model: Optional[str] = None


class ChatCreate(BaseModel):
    workspace_id: str
    name: str


class ChatMessageRequest(BaseModel):
    workspace_id: str
    chat_id: Optional[str] = None
    messages: List[Dict[str, Any]]
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    # Optional per-request API keys (sent from UI). Example: {"anthropic": "..."}
    api_keys: Optional[Dict[str, str]] = None


@router.post("/")
async def create_chat(
    chat: ChatCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat"""
    new_chat = Chat(
        id=str(uuid.uuid4()),
        workspace_id=chat.workspace_id,
        name=chat.name
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return {"id": new_chat.id, "name": new_chat.name}


@router.get("/workspace/{workspace_id}")
async def get_chats(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Get all chats for a workspace"""
    chats = db.query(Chat).filter(Chat.workspace_id == workspace_id).all()
    return [{"id": c.id, "name": c.name, "created_at": c.created_at} for c in chats]


@router.get("/{chat_id}")
async def get_chat(
    chat_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific chat with messages"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    
    return {
        "id": chat.id,
        "name": chat.name,
        "workspace_id": chat.workspace_id,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "model": m.model,
                "created_at": m.created_at
            }
            for m in messages
        ]
    }


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    db: Session = Depends(get_db)
):
    """Delete a chat"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted"}


@router.post("/chat")
async def chat(
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """Send a chat message and get response"""
    chat_service = ChatService(db)
    
    # Get or create chat
    chat = None
    if request.chat_id:
        chat = db.query(Chat).filter(Chat.id == request.chat_id).first()
    
    if not chat and request.workspace_id:
        # Create new chat
        chat = Chat(
            id=str(uuid.uuid4()),
            workspace_id=request.workspace_id,
            name="New Chat"
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
    
    # Add user message
    user_message = Message(
        id=str(uuid.uuid4()),
        chat_id=chat.id,
        role="user",
        content=request.messages[-1]["content"] if request.messages else ""
    )
    db.add(user_message)
    db.commit()
    
    # Get AI response
    response_content = await chat_service.get_chat_response(
        messages=request.messages,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        api_keys=request.api_keys
    )
    
    # Save assistant message
    assistant_message = Message(
        id=str(uuid.uuid4()),
        chat_id=chat.id,
        role="assistant",
        content=response_content,
        model=request.model
    )
    db.add(assistant_message)
    db.commit()
    
    return {
        "chat_id": chat.id,
        "message": {
            "role": "assistant",
            "content": response_content
        }
    }


@router.post("/chat/stream")
async def chat_stream(
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """Send a chat message and get streaming response"""
    chat_service = ChatService(db)
    
    # Get or create chat
    chat = None
    if request.chat_id:
        chat = db.query(Chat).filter(Chat.id == request.chat_id).first()
    
    if not chat and request.workspace_id:
        chat = Chat(
            id=str(uuid.uuid4()),
            workspace_id=request.workspace_id,
            name="New Chat"
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
    
    async def event_generator():
        async for chunk in chat_service.get_streaming_response(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            api_keys=request.api_keys
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
