from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from database.models import DocumentChunk
from database.config import get_db
from backend.services.auth import get_current_user
from backend.services.question_answering_service import generate_answer_with_citations

router = APIRouter(tags=["Question Answering"])

# Pydantic schemas
class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's query")

class Citation(BaseModel):
    chunk_id: UUID = Field(..., description="ID of the document chunk")
    content: str = Field(..., description="Content of the chunk")
    source_document: str = Field(..., description="Filename of the source document")

class AnswerResponse(BaseModel):
    answer: str = Field(..., description="Generated answer to the query")
    citations: List[Citation] = Field(..., description="List of citations used to generate the answer")

# Endpoint to handle question answering
@router.post("/answer", response_model=AnswerResponse, status_code=status.HTTP_200_OK)
async def answer_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Accepts a user query, retrieves the top-5 most relevant chunks, and generates a concise answer
    using a large language model with citations to the source chunks.
    """
    try:
        # Generate answer and retrieve citations
        answer, citations = generate_answer_with_citations(query=request.query, db=db)

        # Format citations for response
        formatted_citations = [
            Citation(
                chunk_id=citation["chunk_id"],
                content=citation["content"],
                source_document=citation["source_document"],
            )
            for citation in citations
        ]

        return AnswerResponse(answer=answer, citations=formatted_citations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the query",
        )