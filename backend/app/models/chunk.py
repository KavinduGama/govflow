"""
Chunk Model — stores document text chunks and vector embeddings.
"""

from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.database import Base

if TYPE_CHECKING:
    from app.models.source_document import SourceDocument


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    source_document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False
    )

    # Context tag (e.g. "Step 1", "Eligibility")
    section_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # The actual text
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Embedding using pgvector's Vector type
    # text-embedding-3-small outputs 1536 dimensions by default
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)

    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    source_document: Mapped["SourceDocument"] = relationship("SourceDocument", backref="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk {self.id}>"
