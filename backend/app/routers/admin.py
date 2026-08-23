from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Service, Question, WorkflowStep, RequiredDocument, SourceDocument

router = APIRouter()

@router.get("/admin/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get basic stats for the admin dashboard."""
    return {
        "services": db.query(Service).count(),
        "questions": db.query(Question).count(),
        "workflow_steps": db.query(WorkflowStep).count(),
        "required_documents": db.query(RequiredDocument).count(),
        "source_documents": db.query(SourceDocument).count()
    }

@router.get("/admin/services")
def list_admin_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return services

@router.get("/admin/services/{service_code}/details")
def get_admin_service_details(service_code: str, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.service_code == service_code).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
        
    questions = db.query(Question).filter(Question.service_id == service.id).order_by(Question.order_index).all()
    steps = db.query(WorkflowStep).filter(WorkflowStep.service_id == service.id).order_by(WorkflowStep.step_number).all()
    docs = db.query(RequiredDocument).filter(RequiredDocument.service_id == service.id).all()
    
    return {
        "service": service,
        "questions": questions,
        "steps": steps,
        "documents": docs
    }
