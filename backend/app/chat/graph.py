"""
LangGraph Setup for Tool-Calling Agent
"""

import os
from functools import lru_cache

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.database import DATABASE_URL

from app.chat.state import ConversationState
from app.chat.nodes import agent_node, tool_node

# ==========================================
# ROUTING LOGIC
# ==========================================
def should_continue(state: ConversationState) -> str:
    """
    Decides whether the agent wants to call a tool, or respond to the user.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the LLM makes a tool call, route to the "tools" node
    if last_message.tool_calls:
        return "tools"
        
    # Otherwise, it has responded to the user, so we stop and wait for input
    return END

# ==========================================
# BUILD THE GRAPH
# ==========================================

builder = StateGraph(ConversationState)

# Add our two core agentic nodes
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

# Start with the agent
builder.add_edge(START, "agent")

# After the agent thinks, it decides to either use a tool or end its turn
builder.add_conditional_edges("agent", should_continue)

# After a tool runs, it ALWAYS goes back to the agent to process the result
builder.add_edge("tools", "agent")

# ==========================================
# CHECKPOINTER (conversation memory)
# ==========================================

def _make_checkpointer():
    """
    Postgres in normal use, so conversations survive restarts and are shared by all workers.
    Set CHAT_CHECKPOINTER=memory for tests or quick experiments without a database.
    """
    if os.getenv("CHAT_CHECKPOINTER", "postgres") == "memory":
        return MemorySaver()

    # psycopg 3 wants a plain postgresql:// URL (no SQLAlchemy "+psycopg2" driver suffix)
    conninfo = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
    pool = ConnectionPool(
        conninfo=conninfo,
        max_size=int(os.getenv("CHAT_DB_POOL_SIZE", "10")),
        # Settings PostgresSaver expects on every connection
        kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
        open=True,
    )
    checkpointer = PostgresSaver(pool)
    checkpointer.setup()  # creates/migrates the checkpoint tables; safe to run every startup
    return checkpointer


@lru_cache(maxsize=1)
def get_chat_graph():
    """Build the graph once, on first use (not at import time, so imports never need a database)."""
    return builder.compile(checkpointer=_make_checkpointer())
