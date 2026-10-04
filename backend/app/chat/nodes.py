import json
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from app.chat.state import ConversationState
from app.chat.tools import (
    search_knowledge_base,
    get_eligibility_questions,
    generate_workflow_plan
)

# 1. Define the tools the agent can use
tools = [search_knowledge_base, get_eligibility_questions, generate_workflow_plan]

# 2. Initialize the LLM and bind the tools
llm = ChatOpenAI(
    model=os.getenv("CHAT_MODEL", "gpt-5.5"),
    timeout=float(os.getenv("LLM_TIMEOUT_SECONDS", "60")),  # never hang a request forever
    max_retries=int(os.getenv("LLM_MAX_RETRIES", "2")),       # retries 429s / 5xx with backoff
)
llm_with_tools = llm.bind_tools(tools)

# 3. Create the ToolNode (handles executing the tools automatically)
tool_node = ToolNode(tools)

from app.database import SessionLocal
from app.models import Service

SYSTEM_PROMPT_TEMPLATE = """
You are GovFlow AI, an intelligent and autonomous assistant for Sri Lankan citizens.
Your job is to help users navigate government procedures or answer their general questions.

You have access to several tools:
1. `search_knowledge_base`: Use this to answer general questions (e.g. office hours, general rules, forms).
2. `get_eligibility_questions`: Use this when a user wants to start a specific procedure. This tool will return a list of questions you MUST ask the user to determine their eligibility.
3. `generate_workflow_plan`: Once you have asked the user ALL the required eligibility questions and gathered their answers, use this tool to generate the final procedure and document checklist.

Available service codes for `get_eligibility_questions` and `generate_workflow_plan`:
{dynamic_services}

INSTRUCTIONS FOR PROCEDURES:
- If a user asks to do something, find the matching service code above and first call `get_eligibility_questions(service_code)`.
- Then, ask the user the questions ONE BY ONE. Do not overwhelm them.
- When the user answers your question, store that answer in your context.
- Users may answer in Sinhala, Tamil or Singlish (e.g. "ow" = yes, "naha" = no, "ඔව්" = yes, "ஆம்" = yes). Accept these as valid answers; do not ask again.
- Each question has an `answer_type`: send booleans as true/false and numbers as numbers in `user_answers_json`.
- If `generate_workflow_plan` returns an error with `missing_questions`, ask the user those questions, then call it again.
- Once you have collected the answers to ALL the questions returned by `get_eligibility_questions`, YOU MUST call `generate_workflow_plan` with a JSON string of their answers.
- Do NOT generate the workflow yourself. You must use the `generate_workflow_plan` tool.
- The `generate_workflow_plan` tool returns a JSON object. 
- **CRITICAL**: Do NOT summarize the output of `generate_workflow_plan`. The frontend UI will automatically catch the JSON string and render a beautiful UI. Just say "I have generated your workflow plan below."

Be helpful, concise, and professional.
"""

def get_dynamic_system_prompt():
    db = SessionLocal()
    try:
        services = db.query(Service).all()
        services_list = "\n".join([f'- "{s.service_code}": {s.title_en}' for s in services])
        return SYSTEM_PROMPT_TEMPLATE.format(dynamic_services=services_list)
    finally:
        db.close()

def agent_node(state: ConversationState):
    """
    The core agent node that decides what to do next.
    """
    messages = state["messages"]

    # The main prompt is never saved in the conversation state, so add it on every call.
    # (Checking "is messages[0] a SystemMessage?" would wrongly skip it whenever the
    # conversation itself starts with a system note, e.g. the service-page context.)
    messages = [SystemMessage(content=get_dynamic_system_prompt())] + messages

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response],
        "final_workflow": find_workflow_in_current_turn(messages)
    }

def find_workflow_in_current_turn(messages) -> dict | None:
    """
    Return the workflow produced by `generate_workflow_plan` during the CURRENT turn only.

    A turn starts at the latest HumanMessage. Looking further back would re-attach an
    old plan to every later reply in the same conversation.
    """
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            break
        if isinstance(msg, ToolMessage) and msg.name == "generate_workflow_plan":
            try:
                workflow_json = json.loads(msg.content)
            except json.JSONDecodeError:
                continue
            if "steps" in workflow_json:
                return workflow_json
    return None
