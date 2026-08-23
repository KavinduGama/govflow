"""
Question Model — stores the qualifying questions asked to the citizen.
"""

from typing import TYPE_CHECKING, Any
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.service import Service


class Question(Base):
    __tablename__ = "service_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    service_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )

    # Identifies the question in code (e.g., "is_one_day_service", "applicant_age")
    question_key: Mapped[str] = mapped_column(String(100), nullable=False)

    # The actual text shown to the user
    question_text: Mapped[str] = mapped_column(String(500), nullable=False)
    help_text: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Example: "boolean", "select", "number"
    answer_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Order in which questions are asked
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # JSON rule! If this condition is met (or empty), the question is asked.
    condition_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    service: Mapped["Service"] = relationship("Service", backref="questions")

    def __repr__(self) -> str:
        return f"<Question {self.question_key}>"
