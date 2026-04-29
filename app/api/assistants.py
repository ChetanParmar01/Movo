"""
Assistants API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid

from app.db.database import get_db
from app.db.models import Assistant

router = APIRouter()


class AssistantCreate(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    model: str = "gpt-4"
    embedder: Optional[str] = None
    tools: Optional[List[dict]] = None
    file_ids: Optional[List[str]] = None


class AssistantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    model: Optional[str] = None
    embedder: Optional[str] = None
    tools: Optional[List[dict]] = None
    file_ids: Optional[List[str]] = None


@router.get("/workspace/{workspace_id}")
async def get_assistants(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Get all assistants for a workspace"""
    assistants = db.query(Assistant).filter(
        Assistant.workspace_id == workspace_id
    ).all()
    
    return [
        {
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "instructions": a.instructions,
            "model": a.model,
            "created_at": a.created_at
        }
        for a in assistants
    ]


@router.post("/")
async def create_assistant(
    assistant: AssistantCreate,
    db: Session = Depends(get_db)
):
    """Create a new assistant"""
    new_assistant = Assistant(
        id=str(uuid.uuid4()),
        workspace_id=assistant.workspace_id,
        name=assistant.name,
        description=assistant.description,
        instructions=assistant.instructions,
        model=assistant.model,
        embedder=assistant.embedder,
        tools=assistant.tools,
        file_ids=assistant.file_ids
    )
    
    db.add(new_assistant)
    db.commit()
    db.refresh(new_assistant)
    
    return {
        "id": new_assistant.id,
        "name": new_assistant.name
    }


@router.get("/{assistant_id}")
async def get_assistant(
    assistant_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific assistant"""
    assistant = db.query(Assistant).filter(Assistant.id == assistant_id).first()
    
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    return {
        "id": assistant.id,
        "workspace_id": assistant.workspace_id,
        "name": assistant.name,
        "description": assistant.description,
        "instructions": assistant.instructions,
        "model": assistant.model,
        "embedder": assistant.embedder,
        "tools": assistant.tools,
        "file_ids": assistant.file_ids,
        "created_at": assistant.created_at
    }


@router.put("/{assistant_id}")
async def update_assistant(
    assistant_id: str,
    assistant_update: AssistantUpdate,
    db: Session = Depends(get_db)
):
    """Update an assistant"""
    assistant = db.query(Assistant).filter(Assistant.id == assistant_id).first()
    
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    update_data = assistant_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assistant, key, value)
    
    db.commit()
    db.refresh(assistant)
    
    return {"id": assistant.id, "name": assistant.name}


@router.delete("/{assistant_id}")
async def delete_assistant(
    assistant_id: str,
    db: Session = Depends(get_db)
):
    """Delete an assistant"""
    assistant = db.query(Assistant).filter(Assistant.id == assistant_id).first()
    
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    db.delete(assistant)
    db.commit()
    
    return {"message": "Assistant deleted"}