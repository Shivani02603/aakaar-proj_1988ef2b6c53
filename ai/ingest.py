import os
import tempfile
from fastapi import UploadFile
import tiktoken
from pypdf import PdfReader
from .embeddings import get_embedding
import psycopg2
from psycopg2.extras import Json

async def chunk(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    enc = tiktoken.get_encoding('cl100k_base')
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += chunk_size - chunk_overlap
    return chunks

async def ingest_pdf(file: UploadFile, session_id: str, user_id: str):
    contents = await file.read()
    original_filename = file.filename or "uploaded_file.pdf"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(original_filename)[1])
    tmp.write(contents)
    tmp.flush()
    file_path = tmp.name

    try:
        reader = PdfReader(file_path)
        text_by_page = [page.extract_text() for page in reader.pages]
        all_chunks = []
        for page_number, page_text in enumerate(text_by_page):
            page_chunks = await chunk(page_text)
            for i, chunk_text in enumerate(page_chunks):
                metadata = {
                    'source_filename': original_filename,
                    'chunk_index': i,
                    'total_chunks': len(page_chunks),
                    'page_or_row': f"Page {page_number + 1}"
                }
                embedding = await get_embedding(chunk_text)
                all_chunks.append((chunk_text, embedding, metadata))

        # Store chunks in PostgreSQL with pgvector
        conn = psycopg2.connect(os.getenv("POSTGRES_CONNECTION_STRING"))
        cursor = conn.cursor()
        for chunk_text, embedding, metadata in all_chunks:
            cursor.execute(
                "INSERT INTO document_chunks (session_id, user_id, chunk_text, embedding, metadata) VALUES (%s, %s, %s, %s, %s)",
                (session_id, user_id, chunk_text, embedding, Json(metadata))
            )
        conn.commit()
        cursor.close()
        conn.close()
    finally:
        os.unlink(file_path)