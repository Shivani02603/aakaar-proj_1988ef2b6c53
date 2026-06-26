from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from database.models import Document, DocumentChunk
from database.config import get_db
from backend.services.document_processing_service import (
    extract_text_from_pdf,
    split_text_into_chunks,
    generate_embeddings,
)
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["Document Processing"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class DocumentBase(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    file_path: str
    file_size: int
    status: str
    created_at: str
    processed_at: str


class DocumentChunkBase(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    embedding: List[float]
    metadata: dict
    created_at: str


class DocumentCreate(BaseModel):
    user_id: UUID
    filename: str
    file_path: str
    file_size: int


class DocumentResponse(DocumentBase):
    pass


class DocumentChunkResponse(DocumentChunkBase):
    pass


@router.post("/process", response_model=List[DocumentChunkResponse], status_code=status.HTTP_201_CREATED)
async def process_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Endpoint to process a document: extract text, split into chunks, and generate embeddings.
    """
    try:
        # Save the uploaded file to a temporary location
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(file_path)

        # Split text into chunks
        chunks = split_text_into_chunks(extracted_text, chunk_size=1000, overlap=200)

        # Generate embeddings for each chunk
        embeddings = generate_embeddings(chunks)

        # Create a new Document entry in the database
        document = Document(
            user_id=UUID(token),  # Assuming token contains user_id
            filename=file.filename,
            file_path=file_path,
            file_size=len(file.file.read()),
            status="processed",
            created_at=datetime.utcnow(),
            processed_at=datetime.utcnow(),
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # Create DocumentChunk entries in the database
        document_chunks = []
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=embedding,
                metadata={},
                created_at=datetime.utcnow(),
            )
            db.add(document_chunk)
            document_chunks.append(document_chunk)

        db.commit()

        return document_chunks

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
async def list_documents(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Endpoint to list all documents for the authenticated user.
    """
    try:
        user_id = UUID(token)  # Assuming token contains user_id
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def get_document(document_id: UUID, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Endpoint to retrieve a specific document by ID.
    """
    try:
        user_id = UUID(token)  # Assuming token contains user_id
        document = db.query(Document).filter(Document.id == document_id, Document.user_id == user_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: UUID, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Endpoint to delete a specific document by ID.
    """
    try:
        user_id = UUID(token)  # Assuming token contains user_id
        document = db.query(Document).filter(Document.id == document_id, Document.user_id == user_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete associated chunks
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

        # Delete the document
        db.delete(document)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")