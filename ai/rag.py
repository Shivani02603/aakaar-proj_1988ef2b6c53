import os
from .embeddings import get_embedding
import psycopg2
import openai

async def retrieve_context(query: str, top_k: int, session_id: str, user_id: str):
    embedding = await get_embedding(query)
    conn = psycopg2.connect(os.getenv("POSTGRES_CONNECTION_STRING"))
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT chunk_text, metadata, embedding <-> %s AS distance
        FROM document_chunks
        WHERE session_id = %s AND user_id = %s
        ORDER BY distance ASC
        LIMIT %s
        """,
        (embedding, session_id, user_id, top_k)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{'chunk_text': row[0], 'metadata': row[1]} for row in results]

async def answer_question(query: str, session_id: str, user_id: str) -> dict:
    context_chunks = await retrieve_context(query, top_k=5, session_id=session_id, user_id=user_id)
    if not context_chunks:
        return {'answer': "No relevant information found.", 'sources': []}

    prompt = "Answer the following question based on the provided context:\n\n"
    for chunk in context_chunks:
        prompt += f"Context: {chunk['chunk_text']}\n\n"
    prompt += f"Question: {query}\n\nProvide a concise answer with citations."

    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{'role': 'user', 'content': prompt}]
    )
    answer = response.choices[0].message.content

    sources = [{'filename': chunk['metadata']['source_filename'], 'location': chunk['metadata']['page_or_row']} for chunk in context_chunks]
    return {'answer': answer, 'sources': sources}