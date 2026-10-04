import logging
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db, get_session_factory
from app.models import Service, Question, WorkflowStep, RequiredDocument, SourceDocument, DocumentChunk, SyncRun, User
from app.services.ingestion import get_knowledge_base_stats
from app.services.sync_jobs import SyncAlreadyRunningError, create_sync_run, execute_sync_run
from app.auth_utils import require_admin
from app.rate_limit import limiter, SCRAPE_SYNC_LIMIT

logger = logging.getLogger(__name__)

# Every route on this router requires a logged-in admin
router = APIRouter(dependencies=[Depends(require_admin)])

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

@router.post("/admin/scrape-sync", status_code=202)
@limiter.limit(SCRAPE_SYNC_LIMIT)
def trigger_scrape_sync(
    request: Request,
    background_tasks: BackgroundTasks,
    # Only sites the ingestion pipeline actually supports; anything else is a 422, not a silent NIC sync
    site: Literal["nic"] = Query(default="nic", description="Site key to scrape/sync"),
    force_live: bool = Query(default=True, description="Whether to attempt live scraping before sync"),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
    admin: User = Depends(require_admin),
):
    """
    Queue a scrape & knowledge-base sync and return immediately (202 Accepted).
    Poll GET /admin/sync-runs/{id} for progress and the result summary.
    """
    try:
        run = create_sync_run(db, site=site, force_live=force_live, user_id=admin.id)
    except SyncAlreadyRunningError as e:
        raise HTTPException(
            status_code=409,
            detail={"message": "A sync is already in progress.", "run": e.run.to_dict()},
        )
    background_tasks.add_task(execute_sync_run, run.id, session_factory)
    return run.to_dict()


@router.get("/admin/sync-runs")
def list_sync_runs(limit: int = Query(default=10, ge=1, le=50), db: Session = Depends(get_db)):
    """Most recent sync runs first."""
    runs = db.query(SyncRun).order_by(SyncRun.created_at.desc(), SyncRun.id.desc()).limit(limit).all()
    return [r.to_dict() for r in runs]


@router.get("/admin/sync-runs/{run_id}")
def get_sync_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(SyncRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Sync run not found")
    return run.to_dict()

@router.get("/admin/knowledge-base/stats")
def get_kb_stats(db: Session = Depends(get_db)):
    """Get vector knowledge base statistics, document breakdown, and last sync timestamp."""
    try:
        return get_knowledge_base_stats(db)
    except Exception:
        logger.exception("Failed to fetch knowledge base stats")
        raise HTTPException(status_code=500, detail="Failed to fetch knowledge base stats.")

