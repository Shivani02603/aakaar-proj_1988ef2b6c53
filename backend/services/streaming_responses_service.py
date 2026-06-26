import uuid
from typing import List, Optional
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import ChatMessage
from database.config import get_db

class StreamingResponsesService:
    @staticmethod
    def create_message(session_id: uuid.UUID, role: str, content: str, metadata: Optional[dict], db: Session = Depends(get_db)) -> ChatMessage:
        """
        Create a new chat message in the database.
        """
        new_message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata,
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return new_message

    @staticmethod
    def get_message_by_id(message_id: uuid.UUID, db: Session = Depends(get_db)) -> ChatMessage:
        """
        Retrieve a chat message by its ID.
        """
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        return message

    @staticmethod
    def list_all_messages(session_id: uuid.UUID, db: Session = Depends(get_db)) -> List[ChatMessage]:
        """
        List all messages for a given chat session.
        """
        messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()
        return messages

    @staticmethod
    def update_message(message_id: uuid.UUID, content: Optional[str], metadata: Optional[dict], db: Session = Depends(get_db)) -> ChatMessage:
        """
        Update an existing chat message.
        """
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        
        if content is not None:
            message.content = content
        if metadata is not None:
            message.metadata = metadata
        
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def delete_message(message_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        """
        Delete a chat message by its ID.
        """
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        
        db.delete(message)
        db.commit()

    @staticmethod
    def stream_answer(session_id: uuid.UUID, typing_indicator: str, db: Session = Depends(get_db)) -> None:
        """
        Stream answer tokens to the frontend in real-time.
        """
        # This is a placeholder for the streaming logic. In a real implementation, this would involve
        # integrating with a streaming library or protocol to send tokens incrementally to the frontend.
        # For now, we simulate the typing indicator and token streaming.
        try:
            # Simulate typing indicator
            print(f"Session {session_id}: {typing_indicator}")
            
            # Simulate token streaming (replace with actual streaming logic)
            tokens = ["This", "is", "a", "streamed", "response."]
            for token in tokens:
                print(f"Streaming token: {token}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during streaming: {str(e)}")