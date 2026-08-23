"""
Workflow Step Model — a single step in the final procedure list given to the user.
"""

from typing import TYPE_CHECKING, Any
from sqlalchemy import String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.service import Service


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    service_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )

    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # E.g., "Grama Niladhari Office", "DMT Head Office"
    location_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # The magic JSON rule for showing this step!
    condition_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    source_document_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True
    )

    service: Mapped["Service"] = relationship("Service", backref="workflow_steps")
    source_document: Mapped["SourceDocument"] = relationship("SourceDocument")

    def __repr__(self) -> str:
        return f"<Step {self.step_number} - {self.title}>"
