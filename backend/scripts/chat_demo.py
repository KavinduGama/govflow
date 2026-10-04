import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.chat.graph import get_chat_graph

chat_graph = get_chat_graph()

def run_demo():
    print("🤖 Welcome to GovFlow AI Terminal Demo!")
    print("Type your message below. Type 'exit' to quit.\n")
    
    # We use a fixed thread_id so the graph remembers our conversation
    config = {"configurable": {"thread_id": "demo_user_123"}}
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        print("\nThinking...")
        
        # We only pass the NEW message. MemorySaver handles the rest!
        inputs = {"messages": [{"role": "user", "content": user_input}]}
        
        # Run the graph
        for event in chat_graph.stream(inputs, config=config):
            # Print which node is currently running
            for node_name, state_update in event.items():
                pass
                
        # Get the final state to see the AI's response
        state = chat_graph.get_state(config).values
        
        # The AI's reply is the last message in the messages list
        ai_reply = state["messages"][-1]["content"]
        
        print(f"\nGovFlow: {ai_reply}\n")
        
        # If workflow is generated, we are done
        if state.get("status") == "done":
            print("========================================")
            print("Workflow generated! Conversation ended.")
            print("========================================")
            break

if __name__ == "__main__":
    run_demo()
