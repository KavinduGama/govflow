from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any
from sqlalchemy.orm import Session
import uuid

from app.chat.graph import chat_graph
from app.database import get_db
from app.auth_utils import get_optional_user
from app.models import User, ChatSession, ChatMessage, SavedWorkflow

router = APIRouter()

class ChatRequest(BaseModel):
    thread_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    status: str
    final_workflow: dict[str, Any] | None
    questions_progress: dict[str, int] | None

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest, 
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user)
):
    """
    Takes a user message, passes it to LangGraph, and returns the AI's response.
    Saves the messages to the database.
    """
    # 1. Handle DB Session for Chat History
    chat_session = db.query(ChatSession).filter(ChatSession.thread_id == request.thread_id).first()
    
    if not chat_session:
        # Create a new session
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        chat_session = ChatSession(
            thread_id=request.thread_id,
            title=title,
            user_id=current_user.id if current_user else None
        )
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
    
    # Save User Message to DB
    user_msg = ChatMessage(session_id=chat_session.id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()

    # 2. Run LangGraph
    config = {"configurable": {"thread_id": request.thread_id}}
    
    initial_input = {
        "messages": [{"role": "user", "content": request.message}]
    }
    
    try:
        for event in chat_graph.stream(initial_input, config=config):
            for node_name, state_update in event.items():
                pass 
        
        state = chat_graph.get_state(config).values
        messages = state.get("messages", [])
        
        last_message_content = "Error: No response."
        if messages:
            last_message_content = messages[-1].content
            
        # 3. Save AI Message to DB
        final_workflow = state.get("final_workflow")
        ai_msg = ChatMessage(
            session_id=chat_session.id, 
            role="assistant", 
            content=last_message_content,
            workflow=final_workflow
        )
        db.add(ai_msg)
        
        # 4. Auto-save workflow to user's saved plans
        if final_workflow and current_user:
            service_code = final_workflow.get("service_code")
            if service_code:
                # Check if we already have a saved plan for this service for this user
                existing_plan = db.query(SavedWorkflow).filter(
                    SavedWorkflow.user_id == current_user.id,
                    SavedWorkflow.service_code == service_code
                ).first()
                
                if existing_plan:
                    existing_plan.workflow_data = final_workflow
                else:
                    new_plan = SavedWorkflow(
                        user_id=current_user.id,
                        service_code=service_code,
                        workflow_data=final_workflow,
                        progress_data={"steps": {}, "docs": {}}
                    )
                    db.add(new_plan)
        
        db.commit()
        
        return ChatResponse(
            reply=last_message_content,
            status=state.get("status", "unknown"),
            final_workflow=state.get("final_workflow"),
            questions_progress=state.get("questions_progress")
        )

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
