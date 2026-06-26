import os
import uuid
from typing import List, Optional
from fastapi import HTTPException, Depends, UploadFile
from sqlalchemy.orm import Session
from PyPDF2 import PdfReader
from openai.embeddings_utils import get_embedding
from database.models import Document, DocumentChunk
from database.config import get_db

class DocumentProcessingService:
    @staticmethod
    def create_document(user_id: uuid.UUID, filename: str, file_path: str, file_size: int, db: Session) -> Document:
        document = Document(
            id=uuid.uuid4(),
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            status="uploaded",
            created_at=datetime.utcnow(),
            processed_at=None
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_document_by_id(document_id: uuid.UUID, db: Session) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    @staticmethod
    def list_all_documents(user_id: uuid.UUID, db: Session) -> List[Document]:
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        return documents

    @staticmethod
    def update_document_status(document_id: uuid.UUID, status: str, db: Session) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        document.status = status
        document.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def delete_document(document_id: uuid.UUID, db: Session) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        db.delete(document)
        db.commit()

    @staticmethod
    def process_document(document_id: uuid.UUID, db: Session) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract text from the PDF
        try:
            pdf_reader = PdfReader(document.file_path)
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading PDF: {str(e)}")
        
        # Split text into chunks
        chunks = DocumentProcessingService.split_text_into_chunks(full_text, chunk_size=1000, overlap=200)
        
        # Generate embeddings for each chunk
        for index, chunk in enumerate(chunks):
            try:
                embedding = get_embedding(chunk, model="text-embedding-3-small")
                document_chunk = DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding,
                    metadata={},
                    created_at=datetime.utcnow()
                )
                db.add(document_chunk)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")
        
        # Update document status
        document.status = "processed"
        document.processed_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def split_text_into_chunks(text: str, chunk_size: int, overlap: int) -> List[str]:
        tokens = text.split()
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk = " ".join(tokens[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap
        return chunks