import uuid
from typing import List, Dict, Optional
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import DocumentChunk
from database.config import get_db
from openai import ChatCompletion

class QuestionAnsweringService:
    @staticmethod
    def create_chunk(
        document_id: uuid.UUID,
        chunk_index: int,
        content: str,
        embedding: List[float],
        metadata: Dict
    ) -> DocumentChunk:
        """
        Create a new document chunk in the database.
        """
        db: Session = Depends(get_db)
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

    @staticmethod
    def get_chunk_by_id(chunk_id: uuid.UUID) -> DocumentChunk:
        """
        Retrieve a document chunk by its ID.
        """
        db: Session = Depends(get_db)
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")
        return chunk

    @staticmethod
    def list_all_chunks(document_id: uuid.UUID) -> List[DocumentChunk]:
        """
        List all chunks for a given document.
        """
        db: Session = Depends(get_db)
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        return chunks

    @staticmethod
    def update_chunk(
        chunk_id: uuid.UUID,
        content: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict] = None
    ) -> DocumentChunk:
        """
        Update an existing document chunk.
        """
        db: Session = Depends(get_db)
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")
        
        if content:
            chunk.content = content
        if embedding:
            chunk.embedding = embedding
        if metadata:
            chunk.metadata = metadata
        
        db.commit()
        db.refresh(chunk)
        return chunk

    @staticmethod
    def delete_chunk(chunk_id: uuid.UUID) -> None:
        """
        Delete a document chunk by its ID.
        """
        db: Session = Depends(get_db)
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")
        
        db.delete(chunk)
        db.commit()

    @staticmethod
    def answer_query(query: str, top_k: int = 5) -> Dict:
        """
        Accept a user query, retrieve the top-k most relevant chunks, and generate a concise answer
        using a large language model with citations to the source chunks.
        """
        db: Session = Depends(get_db)

        # Retrieve top-k relevant chunks based on embeddings (mocked for simplicity)
        chunks = db.query(DocumentChunk).order_by(DocumentChunk.chunk_index).limit(top_k).all()
        if not chunks:
            raise HTTPException(status_code=404, detail="No relevant chunks found")

        # Prepare context for the LLM
        context = "\n".join([f"Chunk {chunk.chunk_index}: {chunk.content}" for chunk in chunks])

        # Generate answer using LLM (mocked for simplicity)
        try:
            llm_response = ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Answer the following query concisely with citations:\n{query}\n\nContext:\n{context}"}
                ]
            )
            answer = llm_response.choices[0].message["content"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

        # Include citations
        citations = [{"chunk_index": chunk.chunk_index, "content": chunk.content} for chunk in chunks]

        return {
            "answer": answer,
            "citations": citations
        }