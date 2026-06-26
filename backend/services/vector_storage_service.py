import uuid
from typing import List, Optional
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import DocumentChunk
from database.config import get_db

class VectorStorageService:
    @staticmethod
    def create_chunk(
        document_id: uuid.UUID,
        chunk_index: int,
        content: str,
        embedding: List[float],
        metadata: dict,
        db: Session = Depends(get_db)
    ) -> DocumentChunk:
        try:
            new_chunk = DocumentChunk(
                id=uuid.uuid4(),
                document_id=document_id,
                chunk_index=chunk_index,
                content=content,
                embedding=embedding,
                metadata=metadata
            )
            db.add(new_chunk)
            db.commit()
            db.refresh(new_chunk)
            return new_chunk
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create document chunk: {str(e)}")

    @staticmethod
    def get_chunk_by_id(chunk_id: uuid.UUID, db: Session = Depends(get_db)) -> DocumentChunk:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")
        return chunk

    @staticmethod
    def list_all_chunks(document_id: uuid.UUID, db: Session = Depends(get_db)) -> List[DocumentChunk]:
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        if not chunks:
            raise HTTPException(status_code=404, detail="No document chunks found for the given document ID")
        return chunks

    @staticmethod
    def update_chunk(
        chunk_id: uuid.UUID,
        content: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[dict] = None,
        db: Session = Depends(get_db)
    ) -> DocumentChunk:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")
        
        try:
            if content is not None:
                chunk.content = content
            if embedding is not None:
                chunk.embedding = embedding
            if metadata is not None:
                chunk.metadata = metadata
            
            db.commit()
            db.refresh(chunk)
            return chunk
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update document chunk: {str(e)}")

    @staticmethod
    def delete_chunk(chunk_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")
        
        try:
            db.delete(chunk)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete document chunk: {str(e)}")