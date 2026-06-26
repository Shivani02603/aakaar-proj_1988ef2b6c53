import os
import uuid
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    Text,
    JSON,
    TIMESTAMP,
    Index,
    func
)
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase
from pgvector.sqlalchemy import Vector

DATABASE_URL_ENV = "DATABASE_URL"
DATABASE_URL = os.environ[DATABASE_URL_ENV]

# SQLAlchemy Base
class Base(DeclarativeBase):
    pass

# Database engine and session setup
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(bind=engine)

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    documents = relationship("Document", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

# Document model
class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    processed_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User", back_populates="documents")
    document_chunks = relationship("DocumentChunk", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"

# DocumentChunk model
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    document = relationship("Document", back_populates="document_chunks")

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, chunk_index={self.chunk_index})>"

# ChatSession model
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="chat_sessions")
    chat_messages = relationship("ChatMessage", back_populates="session")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, title={self.title})>"

# ChatMessage model
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    session = relationship("ChatSession", back_populates="chat_messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role})>"

# Index definitions
Index("ix_documents_user_id", Document.user_id)
Index("ix_document_chunks_document_id", DocumentChunk.document_id)
Index("ix_chat_sessions_user_id", ChatSession.user_id)
Index("ix_chat_messages_session_id", ChatMessage.session_id)