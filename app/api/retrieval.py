"""
Retrieval API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid

from app.db.database import get_db
from app.db.models import Collection, File, CollectionFile

router = APIRouter()


class CollectionCreate(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str] = None
    embedder: Optional[str] = None


class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    embedder: Optional[str] = None


class FileCreate(BaseModel):
    workspace_id: str
    name: str
    type: str
    mime_type: Optional[str] = None
    size: int
    storage_id: Optional[str] = None


# Collection endpoints
@router.get("/collections/workspace/{workspace_id}")
async def get_collections(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Get all collections for a workspace"""
    collections = db.query(Collection).filter(
        Collection.workspace_id == workspace_id
    ).all()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "file_count": len(c.files) if c.files else 0,
            "created_at": c.created_at
        }
        for c in collections
    ]


@router.post("/collections/")
async def create_collection(
    collection: CollectionCreate,
    db: Session = Depends(get_db)
):
    """Create a new collection"""
    new_collection = Collection(
        id=str(uuid.uuid4()),
        workspace_id=collection.workspace_id,
        name=collection.name,
        description=collection.description,
        embedder=collection.embedder
    )
    
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)
    
    return {"id": new_collection.id, "name": new_collection.name}


@router.delete("/collections/{collection_id}")
async def delete_collection(
    collection_id: str,
    db: Session = Depends(get_db)
):
    """Delete a collection"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    db.delete(collection)
    db.commit()
    
    return {"message": "Collection deleted"}


# File endpoints
@router.get("/files/workspace/{workspace_id}")
async def get_files(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Get all files for a workspace"""
    files = db.query(File).filter(File.workspace_id == workspace_id).all()
    
    return [
        {
            "id": f.id,
            "name": f.name,
            "type": f.type,
            "mime_type": f.mime_type,
            "size": f.size,
            "created_at": f.created_at
        }
        for f in files
    ]


@router.post("/files/")
async def create_file(
    file: FileCreate,
    db: Session = Depends(get_db)
):
    """Create a new file record"""
    new_file = File(
        id=str(uuid.uuid4()),
        workspace_id=file.workspace_id,
        name=file.name,
        type=file.type,
        mime_type=file.mime_type,
        size=file.size,
        storage_id=file.storage_id
    )
    
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    
    return {"id": new_file.id, "name": new_file.name}


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db)
):
    """Delete a file"""
    file = db.query(File).filter(File.id == file_id).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    db.delete(file)
    db.commit()
    
    return {"message": "File deleted"}


# Retrieval endpoint
@router.post("/search")
async def search(
    workspace_id: str,
    query: str,
    collection_ids: Optional[List[str]] = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Search across collections"""
    # TODO: Implement actual embedding-based search
    # This is a placeholder that returns mock results
    
    results = []
    
    if collection_ids:
        collections = db.query(Collection).filter(
            Collection.id.in_(collection_ids),
            Collection.workspace_id == workspace_id
        ).all()
    else:
        collections = db.query(Collection).filter(
            Collection.workspace_id == workspace_id
        ).all()
    
    # Mock retrieval - in production, use embeddings
    for collection in collections[:limit]:
        results.append({
            "collection_id": collection.id,
            "collection_name": collection.name,
            "content": f"Sample content from {collection.name}",
            "score": 0.95
        })
    
    return {"results": results}