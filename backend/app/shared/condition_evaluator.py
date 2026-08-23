"""
Condition Evaluator — evaluates JSON rules against user answers.
"""

from typing import Any

def evaluate_condition(condition: dict | None, answers: dict[str, Any]) -> bool:
    """
    Evaluates a condition JSON object against a dictionary of answers.
    Returns True if the condition passes or is None, False otherwise.
    """
    if not condition:
        return True

    # Legacy simple syntax support
    if "include_if" in condition:
        for key, expected in condition["include_if"].items():
            if isinstance(expected, list):
                if answers.get(key) not in expected:
                    return False
            else:
                if answers.get(key) != expected:
                    return False

    if "exclude_if" in condition:
        for key, bad_value in condition["exclude_if"].items():
            if isinstance(bad_value, list):
                if answers.get(key) in bad_value:
                    return False
            else:
                if answers.get(key) == bad_value:
                    return False

    # Question engine legacy syntax support
    if "only_if_answer" in condition:
        for key, expected_value in condition["only_if_answer"].items():
            if answers.get(key) != expected_value:
                return False
                
    if "only_if_answered" in condition:
        if condition["only_if_answered"] not in answers:
            return False

    # Advanced syntax support
    if "all" in condition:
        for rule in condition["all"]:
            if not _evaluate_rule(rule, answers):
                return False

    if "any" in condition:
        if condition["any"]:
            passed_any = False
            for rule in condition["any"]:
                if _evaluate_rule(rule, answers):
                    passed_any = True
                    break
            if not passed_any:
                return False

    return True


def _evaluate_rule(rule: dict, answers: dict[str, Any]) -> bool:
    field = rule.get("field")
    operator = rule.get("operator", "equals")
    value = rule.get("value")

    if not field:
        return True
        
    actual_value = answers.get(field)

    if operator == "equals":
        return actual_value == value
    elif operator == "not_equals":
        return actual_value != value
    elif operator == "in":
        return isinstance(value, list) and actual_value in value
    elif operator == "not_in":
        return isinstance(value, list) and actual_value not in value
    elif operator == "greater_than":
        return actual_value is not None and actual_value > value
    elif operator == "less_than":
        return actual_value is not None and actual_value < value
    elif operator == "between":
        return isinstance(value, list) and len(value) == 2 and actual_value is not None and value[0] <= actual_value <= value[1]
    elif operator == "exists":
        return actual_value is not None
    elif operator == "not_exists":
        return actual_value is None
        
    return False
