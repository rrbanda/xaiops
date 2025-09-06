import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.graph import StateGraph, START, END, MessagesState
from app.agents.specialists import create_graph_agent, create_vector_agent

def create_supervisor():
    """Create supervisor workflow managing specialized agents."""
    
    graph_agent = create_graph_agent()
    vector_agent = create_vector_agent()
    
    def route_question(state):
        """Simple routing based on keywords with better error handling."""
        messages = state["messages"]
        
        # Handle different message content types
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            content = last_message.content
        else:
            content = last_message.get('content', '')
        
        # Ensure content is a string
        if isinstance(content, list):
            content = ' '.join(str(item) for item in content)
        elif not isinstance(content, str):
            content = str(content)
        
        question = content.lower()
        
        # Simple keyword routing
        if any(word in question for word in ["count", "show", "list", "how many"]):
            print(f"Routing to graph_agent: detected structured query")
            return "graph_agent"
        elif any(word in question for word in ["similar", "related", "like", "find"]):
            print(f"Routing to vector_agent: detected similarity query") 
            return "vector_agent"
        else:
            print(f"Default routing to graph_agent")
            return "graph_agent"
    
    # Build workflow
    workflow = StateGraph(MessagesState)
    workflow.add_node("graph_agent", graph_agent)
    workflow.add_node("vector_agent", vector_agent)
    
    workflow.add_conditional_edges(
        START,
        route_question,
        {
            "graph_agent": "graph_agent",
            "vector_agent": "vector_agent"
        }
    )
    
    workflow.add_edge("graph_agent", END)
    workflow.add_edge("vector_agent", END)
    
    return workflow.compile()

if __name__ == "__main__":
    supervisor = create_supervisor()
    
    result = supervisor.invoke({
        "messages": [{"role": "user", "content": "Count all servers"}]
    })
    
    print(f"Test result: {result['messages'][-1].content}")
