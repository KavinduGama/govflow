"""
Source Document Model — Official sources for procedures.
"""

from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.service import Service


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    service_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    # "webpage", "pdf", "form", "faq"
    source_type: Mapped[str] = mapped_column(String(50), default="webpage")

    last_scraped_at: Mapped[str | None] = mapped_column(String(100), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    department: Mapped["Department"] = relationship("Department", backref="source_documents")
    service: Mapped["Service"] = relationship("Service", backref="source_documents")

    def __repr__(self) -> str:
        return f"<SourceDocument {self.title}>"
