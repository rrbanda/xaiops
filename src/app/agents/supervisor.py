import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.graph import StateGraph, START, END, MessagesState
from app.agents.subgraphs import (
    create_data_subgraph, create_security_subgraph,
    create_performance_subgraph, create_compliance_subgraph,
    create_learning_subgraph, create_orchestrator_subgraph
)
from app.llm_config import get_llm

def create_supervisor():
    """Fixed supervisor - simple routing without react agent."""
    
    def route_query(state):
        """Simple LLM-based routing without tools."""
        user_query = state["messages"][0].content if hasattr(state["messages"][0], 'content') else state["messages"][0]["content"]
        
        llm = get_llm()
        routing_prompt = f"""
        You must route this query to exactly one domain: "{user_query}"
        
        Available domains:
        - data_domain
        - security_domain  
        - performance_domain
        - compliance_domain
        - orchestrator_domain
        
        For security vulnerabilities, threats, or security analysis: security_domain
        For server lists or infrastructure data: data_domain
        For performance monitoring: performance_domain
        For audits or compliance: compliance_domain
        For complex multi-domain queries: orchestrator_domain
        
        Respond with ONLY the domain name. No explanation.
        """
        
        result = llm.invoke(routing_prompt)
        domain = result.content.strip().lower().replace(" ", "_")
        
        # Ensure valid domain
        valid_domains = ["data_domain", "security_domain", "performance_domain", "compliance_domain", "orchestrator_domain"]
        if domain not in valid_domains:
            domain = "data_domain"
        
        print(f"DEBUG: Routing to {domain}")
        return domain
        
        return domain
    
    # Main workflow
    workflow = StateGraph(MessagesState)
    workflow.add_node("data_domain", create_data_subgraph())
    workflow.add_node("security_domain", create_security_subgraph())
    workflow.add_node("performance_domain", create_performance_subgraph())
    workflow.add_node("compliance_domain", create_compliance_subgraph())
    workflow.add_node("orchestrator_domain", create_orchestrator_subgraph())
    
    # Direct routing from START
    workflow.add_conditional_edges(
        START,
        route_query,
        {
            "data_domain": "data_domain",
            "security_domain": "security_domain", 
            "performance_domain": "performance_domain",
            "compliance_domain": "compliance_domain",
            "orchestrator_domain": "orchestrator_domain"
        }
    )
    
    # All subgraphs end the workflow
    workflow.add_edge("data_domain", END)
    workflow.add_edge("security_domain", END)
    workflow.add_edge("performance_domain", END)
    workflow.add_edge("compliance_domain", END)
    workflow.add_edge("orchestrator_domain", END)
    
    return workflow.compile()
