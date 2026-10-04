import dataclasses
import json
import logging

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Service, Question
from app.chat.retriever import search_chunks
from app.engines.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the government knowledge base for answers to general questions about procedures, 
    fees, office hours, or policies.
    """
    chunks = search_chunks(query, top_k=3)
    if not chunks:
        return "No relevant information found in the knowledge base."
        
    context = ""
    for idx, c in enumerate(chunks):
        context += f"\n--- Source {idx+1}: {c['source_title']} ({c['section']}) ---\n{c['content']}\n"
    return context

@tool
def get_eligibility_questions(service_code: str) -> str:
    """
    Fetch the list of eligibility questions that must be asked to a user to determine 
    their requirements for a specific service (e.g. 'nic_first_time', 'dl_renewal').
    Use this to figure out what to ask the user.
    """
    db = SessionLocal()
    try:
        service = db.query(Service).filter(Service.service_code == service_code).first()
        if not service:
            return json.dumps({"error": f"Service {service_code} not found."})
            
        questions = db.query(Question).filter(Question.service_id == service.id).order_by(Question.order_index).all()
        
        q_list = []
        for q in questions:
            q_list.append({
                "question_key": q.question_key,
                "question_text": q.question_text,
                "condition": q.condition_json
            })
            
        return json.dumps({"service": service.title_en, "questions": q_list}, indent=2)
    finally:
        db.close()

@tool
def generate_workflow_plan(service_code: str, user_answers_json: str) -> str:
    """
    Generate the final step-by-step procedure and document checklist based on the user's answers.
    Pass `user_answers_json` as a JSON string mapping question keys to the user's answers (e.g. '{"age_over_18": true}').
    """
    db = SessionLocal()
    try:
        answers = json.loads(user_answers_json)
        engine = WorkflowEngine(db)
        result = engine.generate(service_code, answers)
        
        # Returned as a JSON string; the frontend renders it as the plan UI.
        return json.dumps(dataclasses.asdict(result), indent=2)
    except json.JSONDecodeError:
        return json.dumps({"error": "user_answers_json must be a valid JSON object."})
    except Exception:
        # The model sees this text, and may repeat it to the user — never include internals.
        logger.exception("generate_workflow_plan failed for %s", service_code)
        return json.dumps({"error": "Could not generate the workflow plan. Ask the user to try again."})
    finally:
        db.close()
