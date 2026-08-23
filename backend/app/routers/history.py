from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth_utils import get_current_user
from app.models import User, ChatSession, ChatMessage, SavedWorkflow

router = APIRouter()

@router.get("/history/chats")
def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()
    return [{"thread_id": s.thread_id, "title": s.title, "created_at": s.created_at, "service_code": s.service_code} for s in sessions]

@router.get("/history/chats/{thread_id}")
def get_chat_messages(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(ChatSession.thread_id == thread_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc()).all()
    return [{"role": m.role, "content": m.content, "workflow": m.workflow, "created_at": m.created_at} for m in messages]

@router.delete("/history/chats/{thread_id}")
def delete_chat_session(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(ChatSession.thread_id == thread_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    db.delete(session)
    db.commit()
    return {"status": "success"}

@router.get("/history/plans")
def get_saved_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plans = db.query(SavedWorkflow).filter(SavedWorkflow.user_id == current_user.id).order_by(SavedWorkflow.created_at.desc()).all()
    return [{"id": p.id, "service_code": p.service_code, "workflow_data": p.workflow_data, "created_at": p.created_at} for p in plans]

@router.get("/history/plans/{plan_id}")
def get_saved_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(SavedWorkflow).filter(SavedWorkflow.id == plan_id, SavedWorkflow.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"id": plan.id, "service_code": plan.service_code, "workflow_data": plan.workflow_data, "created_at": plan.created_at}

@router.delete("/history/plans/{plan_id}")
def delete_saved_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(SavedWorkflow).filter(SavedWorkflow.id == plan_id, SavedWorkflow.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    db.delete(plan)
    db.commit()
    return {"status": "success"}

from pydantic import BaseModel
class ProgressUpdateRequest(BaseModel):
    progress_data: dict

@router.put("/history/plans/{service_code}/progress")
def update_plan_progress(
    service_code: str,
    request: ProgressUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(SavedWorkflow).filter(SavedWorkflow.service_code == service_code, SavedWorkflow.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    plan.progress_data = request.progress_data
    db.commit()
    return {"status": "success"}
