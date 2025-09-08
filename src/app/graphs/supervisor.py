import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.graph import StateGraph, START, END, MessagesState
from app.graphs.domain_subgraphs import (
    create_data_subgraph, create_security_subgraph,
    create_performance_subgraph, create_compliance_subgraph,
    create_learning_subgraph
)
from app.graphs.rca_subgraph import create_rca_subgraph
from app.graphs.a2a_orchestrator_subgraph import create_a2a_orchestrator_subgraph

def extract_user_query(state):
    """Helper function to safely extract user query from state"""
    first_message = state["messages"][-1]
    
    if isinstance(first_message, dict):
        content = first_message.get("content", "")
    else:
        content = getattr(first_message, 'content', "")
    
    if isinstance(content, list):
        content = " ".join(str(item) for item in content)
    elif not isinstance(content, str):
        content = str(content)
    
    return content

def create_supervisor():
    """Enhanced supervisor with A2A orchestrator integration"""
    
    def route_query(state):
        """Simple, reliable routing function that delegates to A2A orchestrator when needed"""
        user_query = extract_user_query(state)
        query_lower = user_query.lower()
        
        print(f"DEBUG: Routing query: '{user_query}'")
        
        # A2A orchestrator routing - for external/current information
        if any(word in query_lower for word in ["latest", "current", "recent", "news", "today", "search", "web"]):
            print(f"DEBUG: External routing to A2A orchestrator")
            return "a2a_orchestrator_domain"
        
        # Internal ops domain routing (your existing working logic)
        if any(word in query_lower for word in ["security", "vulnerability", "vulnerabilities", "threat", "threats", "compliance", "cve", "ssh", "disable", "enable", "block", "allow", "patch", "remove", "delete", "modify"]):
            print(f"DEBUG: Security domain routing")
            return "security_domain"
        elif any(word in query_lower for word in ["incident", "rca", "troubleshoot", "analyze", "investigation", "root cause"]):
            print(f"DEBUG: RCA domain routing")
            return "rca_domain"
        elif any(word in query_lower for word in ["performance", "monitor", "monitoring", "metric", "metrics", "optimization"]):
            print(f"DEBUG: Performance domain routing")
            return "performance_domain"
        elif any(word in query_lower for word in ["compliance", "audit", "auditing", "policy", "policies", "regulation"]):
            print(f"DEBUG: Compliance domain routing")
            return "compliance_domain"
        elif any(word in query_lower for word in ["learn", "learning", "pattern", "patterns", "knowledge", "update"]):
            print(f"DEBUG: Learning domain routing")
            return "learning_domain"
        else:
            # Default to data domain for infrastructure, servers, databases, etc.
            print(f"DEBUG: Default data domain routing")
            return "data_domain"
    
    def supervisor_node(state):
        """Supervisor node that adds routing info to state"""
        user_query = extract_user_query(state)
        return {
            "messages": [
                {
                    "role": "assistant", 
                    "content": f"Analyzing query: '{user_query}' and routing to appropriate domain...", 
                    "name": "supervisor"
                }
            ]
        }
    
    # Main workflow
    workflow = StateGraph(MessagesState)
    workflow.add_node("supervisor", supervisor_node)
    
    # Add all existing internal domains
    workflow.add_node("data_domain", create_data_subgraph())
    workflow.add_node("security_domain", create_security_subgraph())
    workflow.add_node("performance_domain", create_performance_subgraph())
    workflow.add_node("compliance_domain", create_compliance_subgraph())
    workflow.add_node("learning_domain", create_learning_subgraph())
    workflow.add_node("rca_domain", create_rca_subgraph())
    
    # Add A2A orchestrator domain for external information
    workflow.add_node("a2a_orchestrator_domain", create_a2a_orchestrator_subgraph())
    
    # Flow: Start -> Supervisor -> Route to appropriate domain -> End
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_query,
        {
            "data_domain": "data_domain",
            "security_domain": "security_domain", 
            "performance_domain": "performance_domain",
            "compliance_domain": "compliance_domain",
            "learning_domain": "learning_domain",
            "rca_domain": "rca_domain",
            "a2a_orchestrator_domain": "a2a_orchestrator_domain"
        }
    )
    
    # All domains end the workflow
    workflow.add_edge("data_domain", END)
    workflow.add_edge("security_domain", END)
    workflow.add_edge("performance_domain", END)
    workflow.add_edge("compliance_domain", END)
    workflow.add_edge("learning_domain", END)
    workflow.add_edge("rca_domain", END)
    workflow.add_edge("a2a_orchestrator_domain", END)
    
    return workflow.compile()