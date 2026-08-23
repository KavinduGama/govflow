import argparse
import os
import sys
from openai import OpenAI
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import SourceDocument, DocumentChunk

# Add project root to path so we can run from anywhere
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

client = OpenAI()

def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def chunk_text(text: str, chunk_size=1000) -> list[str]:
    # Extremely basic chunking strategy for MVP
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1 # +1 for space
        if current_length > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def process_documents(db: Session, reset: bool = False):
    if reset:
        print("Resetting existing chunks...")
        db.query(DocumentChunk).delete()
        db.commit()

    docs = db.query(SourceDocument).all()
    print(f"Found {len(docs)} documents to process.")

    for doc in docs:
        print(f"Processing {doc.title}...")
        
        # In a real app we'd fetch the URL content or PDF.
        # For this MVP, we'll just mock some text based on the title.
        mock_content = f"This is the official procedure for {doc.title}. " * 20
        
        chunks = chunk_text(mock_content)
        for i, chunk_text_data in enumerate(chunks):
            embedding = embed_text(chunk_text_data)
            
            chunk = DocumentChunk(
                source_document_id=doc.id,
                section_title=f"Section {i+1}",
                content=chunk_text_data,
                embedding=embedding
            )
            db.add(chunk)
            
        print(f"  -> Created {len(chunks)} chunks.")
    
    db.commit()
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Delete existing chunks first")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        process_documents(db, reset=args.reset)
    finally:
        db.close()
