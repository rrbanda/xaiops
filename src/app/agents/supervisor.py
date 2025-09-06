import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.graph import StateGraph, START, END, MessagesState
from app.agents.subgraphs import (
    create_data_subgraph, create_security_subgraph,
    create_performance_subgraph, create_compliance_subgraph,
    create_learning_subgraph
)
from app.llm_config import get_llm

def create_supervisor():
    """Clean supervisor with proper node/routing separation."""
    
    def route_query(state):
        """Routing function for conditional edges."""
        user_query = state["messages"][0].content if hasattr(state["messages"][0], 'content') else state["messages"][0]["content"]
        
        llm = get_llm()
        routing_prompt = f"""
        You must route this query to exactly one domain: "{user_query}"
        
        Available domains:
        - data_domain
        - security_domain  
        - performance_domain
        - compliance_domain
        
        For security vulnerabilities, threats, or security analysis: security_domain
        For server lists or infrastructure data: data_domain
        For performance monitoring: performance_domain
        For audits or compliance: compliance_domain
        
        Respond with ONLY the domain name. No explanation.
        """
        
        result = llm.invoke(routing_prompt)
        domain = result.content.strip().lower().replace(" ", "_")
        
        # Ensure valid domain
        valid_domains = ["data_domain", "security_domain", "performance_domain", "compliance_domain", "learning_domain"]
        if domain not in valid_domains:
            domain = "data_domain"
        
        print(f"DEBUG: Routing to {domain}")
        return domain
    
    def supervisor_node(state):
        """Supervisor node that adds routing info to state."""
        return {"messages": [{"role": "assistant", "content": "Analyzing query...", "name": "supervisor"}]}
    
    # Main workflow
    workflow = StateGraph(MessagesState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("data_domain", create_data_subgraph())
    workflow.add_node("security_domain", create_security_subgraph())
    workflow.add_node("performance_domain", create_performance_subgraph())
    workflow.add_node("compliance_domain", create_compliance_subgraph())
    workflow.add_node("learning_domain", create_learning_subgraph())
    
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_query,
        {
            "data_domain": "data_domain",
            "security_domain": "security_domain", 
            "performance_domain": "performance_domain",
            "compliance_domain": "compliance_domain",
            "learning_domain": "learning_domain"
        }
    )
    
    # All subgraphs end the workflow
    workflow.add_edge("data_domain", END)
    workflow.add_edge("security_domain", END)
    workflow.add_edge("performance_domain", END)
    workflow.add_edge("compliance_domain", END)
    workflow.add_edge("learning_domain", END)
    
    return workflow.compile()
