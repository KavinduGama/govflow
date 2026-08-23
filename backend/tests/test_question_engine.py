import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Department, Service, Question
from app.engines.question_engine import QuestionEngine

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
    
    q1 = Question(
        service_id=1, question_key="applicant_age", question_text="What is your age?",
        answer_type="number", order_index=1, condition_json=None
    )
    q2 = Question(
        service_id=1, question_key="guardian_consent", question_text="Do you have guardian consent?",
        answer_type="boolean", order_index=2,
        condition_json={"only_if_answer": {"applicant_age": "15"}}
    )
    q3 = Question(
        service_id=1, question_key="is_one_day_service", question_text="Do you want one-day service?",
        answer_type="boolean", order_index=3, condition_json=None
    )
    session.add_all([q1, q2, q3])
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_first_question_returned_with_no_answers(db):
    engine = QuestionEngine(db)
    result = engine.get_next_question("nic_first_time", {})
    
    assert result.next_question is not None
    assert result.next_question.key == "applicant_age"


def test_second_question_after_first_answered(db):
    engine = QuestionEngine(db)
    answers = {"applicant_age": "25"}
    result = engine.get_next_question("nic_first_time", answers)
    
    assert result.next_question is not None
    assert result.next_question.key == "is_one_day_service"


def test_conditional_question_shown_when_condition_met(db):
    engine = QuestionEngine(db)
    answers = {"applicant_age": "15"}
    result = engine.get_next_question("nic_first_time", answers)
    
    assert result.next_question is not None
    assert result.next_question.key == "guardian_consent"


def test_no_question_when_all_answered(db):
    engine = QuestionEngine(db)
    answers = {
        "applicant_age": "25",
        "is_one_day_service": True,
    }
    result = engine.get_next_question("nic_first_time", answers)
    
    assert result.next_question is None
    assert result.questions_remaining == 0
