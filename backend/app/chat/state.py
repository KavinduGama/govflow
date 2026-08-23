"""
LangGraph State Definition
"""
from typing import TypedDict, Any, Annotated
import operator
from langchain_core.messages import BaseMessage, AnyMessage
from langgraph.graph.message import add_messages

class ConversationState(TypedDict):
    """
    Agentic LangGraph state.
    Instead of hardcoded intents and fields, we rely primarily on the message history.
    """
    
    # Message history containing HumanMessage, AIMessage, and ToolMessage
    messages: Annotated[list[AnyMessage], add_messages]
    
    # We keep these fields so the frontend can still render the custom UI when the agent provides them
    final_workflow: dict[str, Any] | None
    
    # Debugging / System flag
    status: str | None
