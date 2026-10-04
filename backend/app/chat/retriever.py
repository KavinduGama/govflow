from typing import List
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import DocumentChunk
from app.database import SessionLocal

_client = None

def _get_client():
    global _client
    if _client is None:
        # Embedding calls are small; fail fast instead of holding the chat request open
        _client = OpenAI(timeout=15.0, max_retries=2)
    return _client

def get_embedding(text: str) -> list[float]:
    response = _get_client().embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search_chunks(query: str, service_code: str = None, top_k: int = 3) -> list[dict]:
    """
    Search for relevant chunks using pgvector and cosine distance.
    If service_code is provided, we can filter, but for MVP we'll just do a global semantic search
    and let the LLM figure it out.
    """
    query_embedding = get_embedding(query)
    
    # We use <=> for cosine distance in pgvector
    # Lower is better (closer)
    
    # Since we might not have a direct link from chunk -> service easily accessible in a simple query 
    # without joining, let's just do a simple vector search for the MVP.
    
    with SessionLocal() as db:
        # Convert the embedding list to a postgres array string
        embedding_str = str(query_embedding).replace(' ', '')
        
        sql = """
            SELECT c.id, c.content, c.section_title, s.title, c.embedding <=> :embedding AS distance
            FROM document_chunks c
            JOIN source_documents s ON c.source_document_id = s.id
            ORDER BY distance ASC
            LIMIT :limit
        """
        
        result = db.execute(text(sql), {"embedding": embedding_str, "limit": top_k})
        
        chunks = []
        for row in result:
            chunks.append({
                "id": row.id,
                "content": row.content,
                "section": row.section_title,
                "source_title": row.title,
                "distance": row.distance
            })
            
        return chunks
