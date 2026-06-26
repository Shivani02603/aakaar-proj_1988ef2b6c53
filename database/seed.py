import uuid
from sqlalchemy.exc import SQLAlchemyError
from database.models import Base, engine, SessionLocal, User, Document, DocumentChunk, ChatSession, ChatMessage

def seed_data():
    session = SessionLocal()
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)

        # Seed Users
        user1 = User(
            id=str(uuid.uuid4()),
            email="alice@example.com",
            hashed_password="hashed_password_1"
        )
        user2 = User(
            id=str(uuid.uuid4()),
            email="bob@example.com",
            hashed_password="hashed_password_2"
        )
        user3 = User(
            id=str(uuid.uuid4()),
            email="charlie@example.com",
            hashed_password="hashed_password_3"
        )
        session.add_all([user1, user2, user3])
        session.commit()

        # Seed Documents
        document1 = Document(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            filename="document1.pdf",
            file_path="/files/document1.pdf",
            file_size=1024,
            status="processed"
        )
        document2 = Document(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            filename="document2.pdf",
            file_path="/files/document2.pdf",
            file_size=2048,
            status="processed"
        )
        document3 = Document(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            filename="document3.pdf",
            file_path="/files/document3.pdf",
            file_size=4096,
            status="processing"
        )
        session.add_all([document1, document2, document3])
        session.commit()

        # Seed DocumentChunks
        chunk1 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document1.id,
            chunk_index=0,
            content="This is the first chunk of document1.",
            embedding=[0.1] * 1536
        )
        chunk2 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document2.id,
            chunk_index=0,
            content="This is the first chunk of document2.",
            embedding=[0.2] * 1536
        )
        chunk3 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document3.id,
            chunk_index=0,
            content="This is the first chunk of document3.",
            embedding=[0.3] * 1536
        )
        session.add_all([chunk1, chunk2, chunk3])
        session.commit()

        # Seed ChatSessions
        session1 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            title="Alice's first chat"
        )
        session2 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            title="Bob's first chat"
        )
        session3 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            title="Charlie's first chat"
        )
        session.add_all([session1, session2, session3])
        session.commit()

        # Seed ChatMessages
        message1 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session1.id,
            role="user",
            content="Hello, how are you?"
        )
        message2 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session2.id,
            role="assistant",
            content="I'm good, thank you!"
        )
        message3 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session3.id,
            role="system",
            content="Welcome to the chat system."
        )
        session.add_all([message1, message2, message3])
        session.commit()

        print("Database seeded successfully!")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()