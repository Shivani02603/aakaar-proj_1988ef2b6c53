import os
import uuid
from typing import List, Optional
from fastapi import HTTPException, Depends, UploadFile
from sqlalchemy.orm import Session
from database.models import Document, User
from database.config import get_db

class DocumentUploadService:
    @staticmethod
    def create_document(user_id: uuid.UUID, filename: str, file_path: str, file_size: int, db: Session = Depends(get_db)) -> Document:
        try:
            new_document = Document(
                id=uuid.uuid4(),
                user_id=user_id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                status="uploaded",
                created_at=datetime.utcnow(),
                processed_at=None
            )
            db.add(new_document)
            db.commit()
            db.refresh(new_document)
            return new_document
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating document: {str(e)}")

    @staticmethod
    def get_document_by_id(document_id: uuid.UUID, db: Session = Depends(get_db)) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    @staticmethod
    def list_documents(user_id: uuid.UUID, db: Session = Depends(get_db)) -> List[Document]:
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        return documents

    @staticmethod
    def update_document_status(document_id: uuid.UUID, status: str, db: Session = Depends(get_db)) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        try:
            document.status = status
            document.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(document)
            return document
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating document status: {str(e)}")

    @staticmethod
    def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        try:
            db.delete(document)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

    @staticmethod
    def upload_file(user_id: uuid.UUID, file: UploadFile, db: Session = Depends(get_db)) -> Document:
        try:
            # Validate file type
            if not file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")

            # Generate file path
            file_id = uuid.uuid4()
            file_path = f"uploads/{file_id}_{file.filename}"
            file_size = len(file.file.read())

            # Save file to disk
            with open(file_path, "wb") as f:
                f.write(file.file.read())

            # Create document record
            return DocumentUploadService.create_document(
                user_id=user_id,
                filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                db=db
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")