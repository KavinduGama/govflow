"""
Question Engine — Deterministic question selection and ordering.
"""

from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models import Service, Question
from app.shared.condition_evaluator import evaluate_condition


@dataclass
class QuestionData:
    """Represents a single question to be asked."""
    id: int
    key: str
    text: str
    help_text: str | None
    answer_type: str
    condition: dict | None


@dataclass 
class QuestionResult:
    """Result returned by the engine."""
    next_question: QuestionData | None   # None means no more questions
    questions_remaining: int
    total_questions: int


class QuestionEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def get_next_question(
        self,
        service_code: str,
        current_answers: dict
    ) -> QuestionResult:
        service = self.db.query(Service).filter(Service.service_code == service_code).first()
        if not service:
            raise ValueError(f"Service not found: {service_code}")
        
        # Load all questions for this service, ordered
        all_questions = (
            self.db.query(Question)
            .filter(Question.service_id == service.id)
            .order_by(Question.order_index)
            .all()
        )
        
        # Filter: only questions whose conditions pass
        applicable_questions = [
            q for q in all_questions
            if evaluate_condition(q.condition_json, current_answers)
        ]
        
        total = len(applicable_questions)
        
        # Find first unanswered question
        for q in applicable_questions:
            if q.question_key not in current_answers:
                return QuestionResult(
                    next_question=QuestionData(
                        id=q.id,
                        key=q.question_key,
                        text=q.question_text,
                        help_text=q.help_text,
                        answer_type=q.answer_type,
                        condition=q.condition_json,
                    ),
                    questions_remaining=sum(
                        1 for qq in applicable_questions
                        if qq.question_key not in current_answers
                    ),
                    total_questions=total
                )
        
        # All questions answered
        return QuestionResult(
            next_question=None,
            questions_remaining=0,
            total_questions=total
        )

