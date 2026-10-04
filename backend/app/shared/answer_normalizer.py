"""
Answer normalizer — turns whatever the agent (or a form) sends into the exact types the rules expect.

Rules compare with ==, <, > ... so "yes" never equals True, and "17" > 16 raises TypeError.
Normalizing once, before any rule runs, makes the rule engine safe no matter who calls it.
"""

from typing import Any

TRUE_WORDS = {"true", "yes", "y", "1", "ow", "ඔව්", "ஆம்"}       # English, Singlish, Sinhala, Tamil
FALSE_WORDS = {"false", "no", "n", "0", "naha", "නැහැ", "இல்லை"}


class InvalidAnswerError(ValueError):
    def __init__(self, question_key: str, value: Any, expected: str):
        super().__init__(f"Answer for '{question_key}' must be {expected}, got {value!r}")
        self.question_key = question_key
        self.expected = expected


def normalize_answer(question_key: str, answer_type: str | None, value: Any) -> Any:
    if value is None:
        return None

    if answer_type == "boolean":
        if isinstance(value, bool):
            return value
        word = str(value).strip().lower()
        if word in TRUE_WORDS:
            return True
        if word in FALSE_WORDS:
            return False
        raise InvalidAnswerError(question_key, value, "yes or no")

    if answer_type == "number":
        if isinstance(value, bool):  # bool is a subclass of int in Python; True is not an age
            raise InvalidAnswerError(question_key, value, "a number")
        if isinstance(value, (int, float)):
            return value
        try:
            number = float(str(value).strip())
        except ValueError:
            raise InvalidAnswerError(question_key, value, "a number") from None
        return int(number) if number.is_integer() else number

    # Free text / choice types (e.g. "district"): trim whitespace, keep the user's wording
    return value.strip() if isinstance(value, str) else value


def normalize_answers(answer_types: dict[str, str | None], answers: dict[str, Any]) -> dict[str, Any]:
    """Normalize every answer whose question we know; pass unknown keys through untouched."""
    return {
        key: normalize_answer(key, answer_types[key], value) if key in answer_types else value
        for key, value in answers.items()
    }
