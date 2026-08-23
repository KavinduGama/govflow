"""
Required Document Model — a document required for a specific service.
"""

from typing import TYPE_CHECKING, Any
from sqlalchemy import String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.service import Service


class RequiredDocument(Base):
    __tablename__ = "required_documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    service_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )

    document_key: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # "required", "optional", "conditional"
    requirement_type: Mapped[str] = mapped_column(String(50), default="required", nullable=False)

    # Condition json similar to questions and workflow steps
    condition_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    source_document_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True
    )

    service: Mapped["Service"] = relationship("Service", backref="required_documents")
    source_document: Mapped["SourceDocument"] = relationship("SourceDocument")

    def __repr__(self) -> str:
        return f"<Document {self.document_key} - {self.name}>"
