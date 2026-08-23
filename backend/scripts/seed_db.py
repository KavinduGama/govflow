"""
Database seeding script.

Run with: python -m scripts.seed_db
Run with --reset to clear existing data first: python -m scripts.seed_db --reset
"""

import json
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Department, Service, Question, WorkflowStep, RequiredDocument, SourceDocument

DATA_DIR = Path(__file__).parent.parent / "data" / "seed"


def load_json(filename: str) -> list:
    path = DATA_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def seed_departments(db: Session):
    print("  Seeding departments...")
    for dept_data in load_json("departments.json"):
        existing = db.query(Department).filter(Department.code == dept_data["code"]).first()
        if not existing:
            dept = Department(**dept_data)
            db.add(dept)
    db.commit()
    print(f"    - Departments: {db.query(Department).count()}")


def seed_services(db: Session):
    print("  Seeding services...")
    for svc_data in load_json("services.json"):
        existing = db.query(Service).filter(Service.service_code == svc_data["service_code"]).first()
        if not existing:
            svc = Service(**svc_data)
            db.add(svc)
    db.commit()
    print(f"    - Services: {db.query(Service).count()}")


def seed_source_documents(db: Session):
    print("  Seeding source documents...")
    docs_file = DATA_DIR / "source_documents.json"
    if not docs_file.exists():
        print("    ⚠ source_documents.json not found, skipping")
        return
    
    for doc_data in load_json("source_documents.json"):
        department_code = doc_data.pop("department_code", None)
        service_code = doc_data.pop("service_code", None)
        
        dept = None
        if department_code:
            dept = db.query(Department).filter(Department.code == department_code).first()
            
        svc = None
        if service_code:
            svc = db.query(Service).filter(Service.service_code == service_code).first()
            
        existing = db.query(SourceDocument).filter(
            SourceDocument.url == doc_data["url"],
            SourceDocument.title == doc_data["title"]
        ).first()
        
        if not existing:
            doc = SourceDocument(
                department_id=dept.id if dept else None,
                service_id=svc.id if svc else None,
                **doc_data
            )
            db.add(doc)
    
    db.commit()
    print(f"    - SourceDocuments: {db.query(SourceDocument).count()}")


def seed_questions(db: Session):
    print("  Seeding questions...")
    for filename in ["nic_questions.json", "dl_questions.json"]:
        docs_file = DATA_DIR / filename
        if not docs_file.exists():
            print(f"    ⚠ {filename} not found, skipping")
            continue
            
        for q_data in load_json(filename):
            service_code = q_data.pop("service_code")
            service = db.query(Service).filter(Service.service_code == service_code).first()
            if not service:
                print(f"    ⚠ Service not found: {service_code}")
                continue
            
            existing = db.query(Question).filter(
                Question.service_id == service.id,
                Question.question_key == q_data["question_key"]
            ).first()
            
            if not existing:
                q = Question(service_id=service.id, **q_data)
                db.add(q)
        
        db.commit()
    print(f"    - Questions: {db.query(Question).count()}")


def seed_workflow_steps(db: Session):
    print("  Seeding workflow steps...")
    steps_file = DATA_DIR / "workflow_steps.json"
    if not steps_file.exists():
        print("    ⚠ workflow_steps.json not found, skipping")
        return
    
    for step_data in load_json("workflow_steps.json"):
        service_code = step_data.pop("service_code")
        service = db.query(Service).filter(Service.service_code == service_code).first()
        if not service:
            print(f"    ⚠ Service not found: {service_code}")
            continue
        
        existing = db.query(WorkflowStep).filter(
            WorkflowStep.service_id == service.id,
            WorkflowStep.step_number == step_data["step_number"],
            WorkflowStep.title == step_data["title"]
        ).first()
        
        if not existing:
            step = WorkflowStep(service_id=service.id, **step_data)
            db.add(step)
    
    db.commit()
    print(f"    - WorkflowSteps: {db.query(WorkflowStep).count()}")


def seed_required_documents(db: Session):
    print("  Seeding required documents...")
    docs_file = DATA_DIR / "required_documents.json"
    if not docs_file.exists():
        print("    ⚠ required_documents.json not found, skipping")
        return
    
    for doc_data in load_json("required_documents.json"):
        service_code = doc_data.pop("service_code")
        service = db.query(Service).filter(Service.service_code == service_code).first()
        if not service:
            print(f"    ⚠ Service not found: {service_code}")
            continue
        
        existing = db.query(RequiredDocument).filter(
            RequiredDocument.service_id == service.id,
            RequiredDocument.document_key == doc_data["document_key"]
        ).first()
        
        if not existing:
            doc = RequiredDocument(service_id=service.id, **doc_data)
            db.add(doc)
    
    db.commit()
    print(f"    - RequiredDocuments: {db.query(RequiredDocument).count()}")


def run(reset: bool = False):
    print("Seeding database...")
    
    if reset:
        print("  ⚠ Resetting data...")
        with SessionLocal() as db:
            db.query(RequiredDocument).delete()
            db.query(SourceDocument).delete()
            db.query(Question).delete()
            db.query(WorkflowStep).delete()
            db.query(Service).delete()
            db.query(Department).delete()
            db.commit()
    
    with SessionLocal() as db:
        seed_departments(db)
        seed_services(db)
        seed_source_documents(db)
        seed_questions(db)
        seed_workflow_steps(db)
        seed_required_documents(db)
    
    print("Seeding complete!")


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    run(reset=reset)

