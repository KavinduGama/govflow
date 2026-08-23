from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Feedback

router = APIRouter()

class FeedbackRequest(BaseModel):
    session_id: str
    is_positive: bool
    comment: str | None = None

class FeedbackResponse(BaseModel):
    status: str
    feedback_id: int

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """Submit thumbs up/down feedback."""
    feedback = Feedback(
        session_id=request.session_id,
        is_positive=request.is_positive,
        comment=request.comment
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return FeedbackResponse(status="success", feedback_id=feedback.id)
