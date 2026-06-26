from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from database.models import DocumentChunk
from database.config import get_db
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["Vector Storage"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Pydantic schemas
class DocumentChunkBase(BaseModel):
    document_id: UUID
    chunk_index: int
    content: str
    embedding: List[float]
    metadata: dict

class DocumentChunkCreate(DocumentChunkBase):
    pass

class DocumentChunkUpdate(BaseModel):
    content: str | None = None
    embedding: List[float] | None = None
    metadata: dict | None = None

class DocumentChunkResponse(DocumentChunkBase):
    id: UUID

    class Config:
        orm_mode = True

# Dependency for JWT authentication
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Placeholder for actual user authentication logic
    # Replace with your JWT validation and user lookup logic
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user

# CRUD endpoints
@router.post("/", response_model=DocumentChunkResponse, status_code=status.HTTP_201_CREATED)
def create_document_chunk(
    chunk: DocumentChunkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_chunk = DocumentChunk(**chunk.dict())
    db.add(db_chunk)
    db.commit()
    db.refresh(db_chunk)
    return db_chunk

@router.get("/", response_model=List[DocumentChunkResponse])
def list_document_chunks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chunks = db.query(DocumentChunk).all()
    return chunks

@router.get("/{chunk_id}", response_model=DocumentChunkResponse)
def get_document_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")
    return chunk

@router.put("/{chunk_id}", response_model=DocumentChunkResponse)
def update_document_chunk(
    chunk_id: UUID,
    chunk_update: DocumentChunkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")
    
    for key, value in chunk_update.dict(exclude_unset=True).items():
        setattr(chunk, key, value)
    
    db.commit()
    db.refresh(chunk)
    return chunk

@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")
    
    db.delete(chunk)
    db.commit()