import uuid
from typing import List, Optional
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import ChatSession, ChatMessage
from database.config import get_db


class ChatHistoryService:
    @staticmethod
    def create_chat_session(user_id: uuid.UUID, title: str, db: Session = Depends(get_db)) -> ChatSession:
        new_session = ChatSession(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session

    @staticmethod
    def get_chat_session_by_id(session_id: uuid.UUID, db: Session = Depends(get_db)) -> ChatSession:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session

    @staticmethod
    def list_chat_sessions(user_id: uuid.UUID, db: Session = Depends(get_db)) -> List[ChatSession]:
        sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
        return sessions

    @staticmethod
    def update_chat_session(session_id: uuid.UUID, title: str, db: Session = Depends(get_db)) -> ChatSession:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        session.title = title
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete_chat_session(session_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        db.delete(session)
        db.commit()

    @staticmethod
    def create_chat_message(session_id: uuid.UUID, role: str, content: str, metadata: Optional[dict], db: Session = Depends(get_db)) -> ChatMessage:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        new_message = ChatMessage(
            id=uuid.uuid4(),
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata or {},
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return new_message

    @staticmethod
    def get_chat_messages_by_session(session_id: uuid.UUID, db: Session = Depends(get_db)) -> List[ChatMessage]:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
        return messages

    @staticmethod
    def delete_chat_message(message_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        db.delete(message)
        db.commit()