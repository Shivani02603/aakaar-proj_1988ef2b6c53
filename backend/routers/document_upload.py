from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from database.models import Document, User
from database.config import get_db
from backend.services.document_upload_service import save_document_metadata, process_uploaded_file
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["Document Upload"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Pydantic Schemas
class DocumentBase(BaseModel):
    filename: str
    file_path: str
    file_size: int
    status: str
    created_at: str
    processed_at: str | None

class DocumentResponse(DocumentBase):
    id: UUID
    user_id: UUID

class DocumentCreate(BaseModel):
    filename: str = Field(..., example="example.pdf")
    file_size: int = Field(..., example=1024)

# Dependency to get the current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return user

# Routes
@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document (PDF) and save its metadata.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

    try:
        # Save file and metadata
        document_metadata = await save_document_metadata(file, current_user.id, db)
        await process_uploaded_file(file, document_metadata.file_path)
        return document_metadata
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    List all documents uploaded by the authenticated user.
    """
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
def get_document(document_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get details of a specific document by ID.
    """
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a specific document by ID.
    """
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    db.delete(document)
    db.commit()
    return {"detail": "Document deleted successfully"}