import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Department, Service, WorkflowStep
from app.engines.workflow_engine import WorkflowEngine

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    
    dept = Department(id=1, code="test_dept", name_en="Test Dept")
    session.add(dept)
    
    service = Service(id=1, department_id=1, service_code="nic_first_time", title_en="NIC First Time")
    session.add(service)
    session.flush()
    
    step1 = WorkflowStep(
        service_id=1, step_number=1, title="Step 1: Always shown",
        condition_json=None
    )
    step2 = WorkflowStep(
        service_id=1, step_number=2, title="Step 2: Only for one day service",
        condition_json={"include_if": {"is_one_day_service": True}}
    )
    step3 = WorkflowStep(
        service_id=1, step_number=3, title="Step 3: Only for normal service",
        condition_json={"include_if": {"is_one_day_service": False}}
    )
    session.add_all([step1, step2, step3])
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_generate_workflow_one_day_service(db):
    engine = WorkflowEngine(db)
    answers = {"is_one_day_service": True}
    result = engine.generate("nic_first_time", answers)
    
    assert result.total_steps == 2
    assert result.steps[0].title == "Step 1: Always shown"
    assert result.steps[1].title == "Step 2: Only for one day service"


def test_generate_workflow_normal_service(db):
    engine = WorkflowEngine(db)
    answers = {"is_one_day_service": False}
    result = engine.generate("nic_first_time", answers)
    
    assert result.total_steps == 2
    assert result.steps[0].title == "Step 1: Always shown"
    assert result.steps[1].title == "Step 3: Only for normal service"
