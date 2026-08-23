from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class SavedWorkflow(Base):
    __tablename__ = "saved_workflows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_code = Column(String, nullable=False)
    workflow_data = Column(JSON, nullable=False)
    progress_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="saved_workflows")

    def __repr__(self) -> str:
        return f"<SavedWorkflow {self.service_code} user={self.user_id}>"
