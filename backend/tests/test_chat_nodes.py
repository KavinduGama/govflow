import json
import os

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

# nodes.py builds the OpenAI client at import time; a dummy key is enough because no call is made.
os.environ.setdefault("OPENAI_API_KEY", "test-key")

from app.chat.nodes import find_workflow_in_current_turn  # noqa: E402

WORKFLOW = {"service_code": "nic_first_time", "steps": [{"step_number": 1}]}


def workflow_tool_message():
    return ToolMessage(
        content=json.dumps(WORKFLOW),
        name="generate_workflow_plan",
        tool_call_id="call_1",
    )


def test_returns_workflow_generated_in_current_turn():
    messages = [
        SystemMessage(content="system"),
        HumanMessage(content="yes, I am over 18"),
        AIMessage(content=""),
        workflow_tool_message(),
    ]
    assert find_workflow_in_current_turn(messages) == WORKFLOW


def test_ignores_workflow_from_previous_turn():
    messages = [
        HumanMessage(content="yes, I am over 18"),
        AIMessage(content=""),
        workflow_tool_message(),
        AIMessage(content="I have generated your workflow plan below."),
        HumanMessage(content="What are the office hours?"),
    ]
    assert find_workflow_in_current_turn(messages) is None


def test_ignores_tool_errors():
    messages = [
        HumanMessage(content="generate it"),
        ToolMessage(content='{"error": "Service not found"}', name="generate_workflow_plan", tool_call_id="c"),
    ]
    assert find_workflow_in_current_turn(messages) is None
