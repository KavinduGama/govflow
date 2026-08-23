from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Service, Question
from app.schemas.service import ServiceResponse, ServiceListResponse

router = APIRouter()


@router.get("/services", response_model=ServiceListResponse)
def list_services(db: Session = Depends(get_db)):
    """List all services."""
    services = db.query(Service).all()
    return ServiceListResponse(services=services, total=len(services))


@router.get("/services/{service_code}", response_model=ServiceResponse)
def get_service(service_code: str, db: Session = Depends(get_db)):
    """Get a single service by its code."""
    service = db.query(Service).filter(Service.service_code == service_code).first()
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_code}' not found")
    return service


@router.get("/services/{service_code}/questions")
def get_service_questions(service_code: str, db: Session = Depends(get_db)):
    """Get all questions for a service."""
    service = db.query(Service).filter(Service.service_code == service_code).first()
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_code}' not found")
    
    questions = (
        db.query(Question)
        .filter(Question.service_id == service.id)
        .order_by(Question.order_index)
        .all()
    )
    
    return {
        "service_code": service_code,
        "questions": [
            {
                "id": q.id,
                "key": q.question_key,
                "text": q.question_text,
                "help_text": q.help_text,
                "answer_type": q.answer_type,
                "condition": q.condition_json,
            }
            for q in questions
        ]
    }
