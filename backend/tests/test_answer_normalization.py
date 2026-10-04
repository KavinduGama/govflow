import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.engines.workflow_engine import MissingAnswersError, WorkflowEngine
from app.models import Department, Question, Service, WorkflowStep
from app.shared.answer_normalizer import InvalidAnswerError, normalize_answer


# ---------- normalize_answer ----------

@pytest.mark.parametrize("raw", [True, "yes", "Yes ", "Y", "true", "1", "ow", "ඔව්", "ஆம்"])
def test_boolean_yes_variants(raw):
    assert normalize_answer("q", "boolean", raw) is True


@pytest.mark.parametrize("raw", [False, "no", "NO", "n", "false", "0", "naha", "නැහැ", "இல்லை"])
def test_boolean_no_variants(raw):
    assert normalize_answer("q", "boolean", raw) is False


def test_unclear_boolean_is_rejected_not_guessed():
    with pytest.raises(InvalidAnswerError):
        normalize_answer("is_one_day_service", "boolean", "maybe")


@pytest.mark.parametrize("raw, expected", [("17", 17), (" 17 ", 17), ("17.5", 17.5), (17, 17), ("18.0", 18)])
def test_numbers(raw, expected):
    assert normalize_answer("age", "number", raw) == expected


@pytest.mark.parametrize("raw", ["seventeen", True])
def test_invalid_numbers_are_rejected(raw):
    with pytest.raises(InvalidAnswerError):
        normalize_answer("age", "number", raw)


def test_text_is_trimmed():
    assert normalize_answer("district", "district", "  Kandy ") == "Kandy"


# ---------- WorkflowEngine with real-world answers ----------

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    session.add(Department(id=1, code="drp", name_en="DRP"))
    session.add(Service(id=1, department_id=1, service_code="nic_first_time", title_en="NIC First Time"))
    session.flush()
    session.add_all([
        Question(service_id=1, question_key="is_one_day_service", question_text="One-day service?",
                 answer_type="boolean", order_index=1),
        Question(service_id=1, question_key="applicant_age", question_text="What is your age?",
                 answer_type="number", order_index=2),
        # Only asked when the applicant is under 18
        Question(service_id=1, question_key="has_guardian", question_text="Will a guardian come with you?",
                 answer_type="boolean", order_index=3,
                 condition_json={"all": [{"field": "applicant_age", "operator": "less_than", "value": 18}]}),
        WorkflowStep(service_id=1, step_number=1, title="One-day counter",
                     condition_json={"include_if": {"is_one_day_service": True}}),
        WorkflowStep(service_id=1, step_number=2, title="Guardian signs the form",
                     condition_json={"all": [{"field": "applicant_age", "operator": "less_than", "value": 18}]}),
    ])
    session.commit()
    yield session
    session.close()


def test_string_answers_from_the_model_still_match_rules(db):
    # Before normalization, "yes" != True dropped step 1, and "17" < 18 raised TypeError
    result = WorkflowEngine(db).generate(
        "nic_first_time", {"is_one_day_service": "yes", "applicant_age": "17", "has_guardian": "yes"}
    )
    assert [s.title for s in result.steps] == ["One-day counter", "Guardian signs the form"]
    assert result.answers_used == {"is_one_day_service": True, "applicant_age": 17, "has_guardian": True}


def test_missing_answer_is_refused(db):
    with pytest.raises(MissingAnswersError) as exc:
        WorkflowEngine(db).generate("nic_first_time", {"is_one_day_service": True})
    assert exc.value.question_keys == ["applicant_age"]


def test_conditional_question_is_only_required_when_it_applies(db):
    # has_guardian only applies under 18, so an adult doesn't need to answer it
    result = WorkflowEngine(db).generate("nic_first_time", {"is_one_day_service": False, "applicant_age": 30})
    assert result.steps == []


def test_conditional_question_is_required_when_it_applies(db):
    with pytest.raises(MissingAnswersError) as exc:
        WorkflowEngine(db).generate("nic_first_time", {"is_one_day_service": False, "applicant_age": 16})
    assert exc.value.question_keys == ["has_guardian"]
