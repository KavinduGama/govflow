from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True) # E.g., the thread ID
    is_positive = Column(Boolean, nullable=False)
    comment = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<Feedback {'👍' if self.is_positive else '👎'}>"
