"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2023-10-11 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
import uuid

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('user_id', sa.String, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('filename', sa.String, nullable=False),
        sa.Column('file_path', sa.String, nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('processed_at', sa.TIMESTAMP, nullable=True),
    )
    op.create_index('ix_documents_user_id', 'documents', ['user_id'])

    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('document_id', sa.String, sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('chunk_index', sa.Integer, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_document_chunks_document_id', 'document_chunks', ['document_id'])

    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('user_id', sa.String, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'])

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('session_id', sa.String, sa.ForeignKey('chat_sessions.id'), nullable=False),
        sa.Column('role', sa.String, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'])


def downgrade():
    # Drop chat_messages table
    op.drop_index('ix_chat_messages_session_id', table_name='chat_messages')
    op.drop_table('chat_messages')

    # Drop chat_sessions table
    op.drop_index('ix_chat_sessions_user_id', table_name='chat_sessions')
    op.drop_table('chat_sessions')

    # Drop document_chunks table
    op.drop_index('ix_document_chunks_document_id', table_name='document_chunks')
    op.drop_table('document_chunks')

    # Drop documents table
    op.drop_index('ix_documents_user_id', table_name='documents')
    op.drop_table('documents')

    # Drop users table
    op.drop_table('users')

    # Disable pgvector extension
    op.execute("DROP EXTENSION IF EXISTS vector;")