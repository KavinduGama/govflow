"""
Service Model — represents a specific citizen procedure.
Examples: 'nic_first_time', 'dl_renewal'
"""

from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.department import Department


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign Key pointing to Department
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False
    )

    # Service fields
    service_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    title_si: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title_ta: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_time: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fee_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship back to Department
    department: Mapped["Department"] = relationship(
        "Department", back_populates="services"
    )

    def __repr__(self) -> str:
        return f"<Service {self.service_code} - {self.title_en}>"
