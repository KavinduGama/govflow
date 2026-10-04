import logging

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Any
from sqlalchemy.orm import Session
import uuid

from app.chat.graph import get_chat_graph
from app.database import get_db
from app.auth_utils import get_optional_user
from app.models import User, ChatSession, ChatMessage, SavedWorkflow, Service
from app.rate_limit import limiter, CHAT_LIMIT

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 2000

class ChatRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)
    # Set when the chat was opened from a service page (/?service=...); only used for a new thread
    service_code: str | None = Field(default=None, max_length=50)

class ChatResponse(BaseModel):
    reply: str
    status: str
    final_workflow: dict[str, Any] | None
    questions_progress: dict[str, int] | None

@router.post("/chat", response_model=ChatResponse)
@limiter.limit(CHAT_LIMIT)
def chat_endpoint(
    request: Request,
    body: ChatRequest,
    
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user)
):
    """
    Takes a user message, passes it to LangGraph, and returns the AI's response.
    Saves the messages to the database.
    """
    # 1. Handle DB Session for Chat History
    chat_session = db.query(ChatSession).filter(ChatSession.thread_id == body.thread_id).first()

    # A thread that belongs to a user can only be continued by that user.
    # 404 rather than 403 so we don't reveal that the thread exists.
    if chat_session and chat_session.user_id is not None:
        if current_user is None or current_user.id != chat_session.user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    
    new_messages = []

    if not chat_session:
        # Only trust service codes that exist; anything else is ignored, not passed to the model
        service = None
        if body.service_code:
            service = db.query(Service).filter(Service.service_code == body.service_code).first()

        # Create a new session
        title = body.message[:50] + "..." if len(body.message) > 50 else body.message
        chat_session = ChatSession(
            thread_id=body.thread_id,
            title=title,
            user_id=current_user.id if current_user else None,
            service_code=service.service_code if service else None,
        )
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)

        if service:
            new_messages.append({
                "role": "system",
                "content": (
                    f'The user opened this chat from the "{service.title_en}" service page '
                    f'(service_code: {service.service_code}). Assume this is the procedure they want '
                    "unless they say otherwise, and start by calling get_eligibility_questions for it."
                ),
            })

    # Save User Message to DB
    user_msg = ChatMessage(session_id=chat_session.id, role="user", content=body.message)
    db.add(user_msg)
    db.commit()

    # 2. Run LangGraph
    config = {"configurable": {"thread_id": body.thread_id}}

    new_messages.append({"role": "user", "content": body.message})
    initial_input = {"messages": new_messages}
    
    try:
        chat_graph = get_chat_graph()
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

    except Exception:
        logger.exception("Chat failed for thread %s", body.thread_id)
        raise HTTPException(
            status_code=500,
            detail="Sorry, something went wrong while answering. Please try again.",
        )
