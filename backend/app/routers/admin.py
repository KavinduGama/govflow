from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Service, Question, WorkflowStep, RequiredDocument, SourceDocument, DocumentChunk
from app.services.ingestion import run_scrape_and_sync, get_knowledge_base_stats

router = APIRouter()

@router.get("/admin/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get basic stats for the admin dashboard."""
    return {
        "services": db.query(Service).count(),
        "questions": db.query(Question).count(),
        "workflow_steps": db.query(WorkflowStep).count(),
        "required_documents": db.query(RequiredDocument).count(),
        "source_documents": db.query(SourceDocument).count(),
        "document_chunks": db.query(DocumentChunk).count()
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

@router.post("/admin/scrape-sync")
def trigger_scrape_sync(
    site: str = Query(default="nic", description="Site key to scrape/sync, e.g. 'nic'"),
    force_live: bool = Query(default=True, description="Whether to attempt live scraping before sync"),
    db: Session = Depends(get_db)
):
    """
    Trigger scraping and vector knowledge base synchronization.
    Runs live scraper (with graceful fallback to cached data), chunks content,
    and updates vector database only for new or modified content.
    """
    try:
        result = run_scrape_and_sync(db=db, site_key=site, force_live=force_live)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scrape & sync failed: {str(e)}")

@router.get("/admin/knowledge-base/stats")
def get_kb_stats(db: Session = Depends(get_db)):
    """Get vector knowledge base statistics, document breakdown, and last sync timestamp."""
    try:
        return get_knowledge_base_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch KB stats: {str(e)}")

