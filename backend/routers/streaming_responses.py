from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Generator
from uuid import UUID
from pydantic import BaseModel, Field
from database.models import ChatSession, ChatMessage
from database.config import get_db
from backend.services.streaming_responses_service import generate_streaming_answer
from fastapi.security import OAuth2PasswordBearer

# OAuth2 dependency for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# APIRouter for Streaming Responses
router = APIRouter(tags=["Streaming Responses"])

# Pydantic schemas
class StreamAnswerRequest(BaseModel):
    session_id: UUID
    question: str

class StreamAnswerResponse(BaseModel):
    role: str
    content: str
    metadata: dict

# Dependency to verify JWT token (mock implementation for now)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> ChatSession:
    # Mock implementation: Replace with actual JWT verification logic
    user = db.query(ChatSession).filter(ChatSession.id == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user

# Streaming response generator
def answer_stream_generator(session_id: UUID, question: str) -> Generator[str, None, None]:
    try:
        for token in generate_streaming_answer(session_id, question):
            yield token
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# POST /api/stream/answer
@router.post("/answer", response_model=None)
async def stream_answer(
    request: StreamAnswerRequest,
    current_user: ChatSession = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Stream the answer tokens to the frontend in real-time.
    """
    # Validate session existence
    session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")

    # Stream response
    return StreamingResponse(
        answer_stream_generator(request.session_id, request.question),
        media_type="text/plain",
    )