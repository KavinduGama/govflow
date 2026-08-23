"""
Department Model — represents a government ministry/department.
Examples: DRP (Registration of Persons), DMT (Motor Traffic)
"""

from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.service import Service


class Department(Base):
    __tablename__ = "departments"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Department fields
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    name_si: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name_ta: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    hotline: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationship to Service table (One Department -> Many Services)
    services: Mapped[List["Service"]] = relationship(
        "Service", back_populates="department", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Department {self.code} - {self.name_en}>"
