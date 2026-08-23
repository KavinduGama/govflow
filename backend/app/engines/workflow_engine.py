"""
Workflow Engine — Generates personalized step lists from user answers.
"""

from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models import Service, WorkflowStep, RequiredDocument
from app.shared.condition_evaluator import evaluate_condition


@dataclass
class WorkflowStepResult:
    id: int
    step_number: int
    title: str
    description: str | None
    location_type: str | None


@dataclass
class DocumentResult:
    document_key: str
    name: str
    description: str | None
    requirement_type: str


@dataclass
class GeneratedWorkflow:
    service_name: str
    service_code: str
    steps: list[WorkflowStepResult]
    documents: list[DocumentResult]
    total_steps: int
    answers_used: dict


class WorkflowEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def generate(self, service_code: str, answers: dict) -> GeneratedWorkflow:
        service = self.db.query(Service).filter(Service.service_code == service_code).first()
        if not service:
            raise ValueError(f"Service not found: {service_code}")
        
        # Get all steps
        all_steps = (
            self.db.query(WorkflowStep)
            .filter(WorkflowStep.service_id == service.id)
            .order_by(WorkflowStep.step_number)
            .all()
        )
        
        # Filter applicable steps
        applicable_steps = [
            WorkflowStepResult(
                id=step.id,
                step_number=step.step_number,
                title=step.title,
                description=step.description,
                location_type=step.location_type
            )
            for step in all_steps
            if evaluate_condition(step.condition_json, answers)
        ]

        # Get all required documents
        all_docs = (
            self.db.query(RequiredDocument)
            .filter(RequiredDocument.service_id == service.id)
            .all()
        )

        # Filter applicable documents
        applicable_docs = [
            DocumentResult(
                document_key=doc.document_key,
                name=doc.name,
                description=doc.description,
                requirement_type=doc.requirement_type
            )
            for doc in all_docs
            if evaluate_condition(doc.condition_json, answers)
        ]
        
        return GeneratedWorkflow(
            service_name=service.title_en,
            service_code=service_code,
            steps=applicable_steps,
            documents=applicable_docs,
            total_steps=len(applicable_steps),
            answers_used=answers,
        )
