from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

ROLE_CITIZEN = "citizen"
ROLE_ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String)
    # "citizen" (default) or "admin". Later phases add editor / reviewer / gov_officer.
    role = Column(String(20), nullable=False, server_default="citizen", default="citizen")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    saved_workflows = relationship("SavedWorkflow", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    def __repr__(self) -> str:
        return f"<User {self.email}>"
