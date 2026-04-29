"""
API Keys API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from app.db.database import get_db
from app.db.models import APIKey

router = APIRouter()


class APIKeyCreate(BaseModel):
    name: str
    type: str  # openai, anthropic, google, etc.
    key: str


class APIKeyUpdate(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None


@router.get("/")
async def get_keys(
    db: Session = Depends(get_db)
):
    """Get all API keys"""
    keys = db.query(APIKey).all()
    
    return [
        {
            "id": k.id,
            "name": k.name,
            "type": k.type,
            "created_at": k.created_at
        }
        for k in keys
    ]


@router.post("/")
async def create_key(
    key: APIKeyCreate,
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    new_key = APIKey(
        id=str(uuid.uuid4()),
        user_id="default",  # TODO: Get from auth
        name=key.name,
        type=key.type,
        key=key.key
    )
    
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    return {"id": new_key.id, "name": new_key.name, "type": new_key.type}


@router.delete("/{key_id}")
async def delete_key(
    key_id: str,
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db.delete(key)
    db.commit()
    
    return {"message": "API key deleted"}