"""
LangGraph Setup for Tool-Calling Agent
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

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

# Compile the graph with memory!
memory = MemorySaver()
chat_graph = builder.compile(checkpointer=memory)
