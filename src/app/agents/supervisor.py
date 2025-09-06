import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END, MessagesState
from app.agents.subgraphs import (
    create_data_subgraph, create_security_subgraph,
    create_performance_subgraph, create_compliance_subgraph,
    create_learning_subgraph, create_orchestrator_subgraph
)
from app.llm_config import get_llm

@tool
def route_to_data_domain(query: str) -> str:
    """Route queries needing structured data and similarity analysis."""
    return f"Routing to data domain: {query}"

@tool
def route_to_security_domain(query: str) -> str:
    """Route security and vulnerability queries."""
    return f"Routing to security domain: {query}"

@tool
def route_to_performance_domain(query: str) -> str:
    """Route performance and monitoring queries."""
    return f"Routing to performance domain: {query}"

@tool
def route_to_compliance_domain(query: str) -> str:
    """Route compliance and audit queries."""
    return f"Routing to compliance domain: {query}"

@tool
def route_to_learning_domain(query: str) -> str:
    """Route to learning analysis for knowledge extraction."""
    return f"Routing to learning domain: {query}"

@tool
def route_to_orchestrator_domain(query: str) -> str:
    """Route complex multi-domain queries requiring cross-domain analysis."""
    return f"Routing to orchestrator domain: {query}"

def create_supervisor():
    """Enhanced supervisor with cross-domain orchestration capability."""
    
    supervisor_agent = create_react_agent(
        model=get_llm(),
        tools=[
            route_to_data_domain, route_to_security_domain,
            route_to_performance_domain, route_to_compliance_domain,
            route_to_learning_domain, route_to_orchestrator_domain
        ],
        prompt=(
            "You are an infrastructure supervisor that routes queries to specialized domains.\n\n"
            "DOMAIN ROUTING:\n"
            "- route_to_data_domain: Server lists, counts, backup configs, general data queries\n"
            "- route_to_security_domain: Vulnerabilities, threats, security analysis\n"
            "- route_to_performance_domain: Performance monitoring, optimization, capacity\n"
            "- route_to_compliance_domain: Audits, regulatory compliance, policies\n"
            "- route_to_learning_domain: Extract patterns, analyze conversations, improve knowledge\n"
            "- route_to_orchestrator_domain: Complex queries spanning multiple domains, holistic analysis\n\n"
            "Use orchestrator for queries like 'comprehensive infrastructure audit', 'root cause analysis',\n"
            "'impact assessment', or when multiple domains are clearly involved.\n"
            "Choose the most appropriate domain based on query context."
        ),
        name="supervisor",
    )
    
    def route_to_subgraph(state):
        """Route to appropriate domain subgraph."""
        last_message = state["messages"][-1]
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            tool_name = last_message.tool_calls[0]["name"]
            if "data_domain" in tool_name:
                return "data_domain"
            elif "security_domain" in tool_name:
                return "security_domain"
            elif "performance_domain" in tool_name:
                return "performance_domain"
            elif "compliance_domain" in tool_name:
                return "compliance_domain"
            elif "learning_domain" in tool_name:
                return "learning_domain"
            elif "orchestrator_domain" in tool_name:
                return "orchestrator_domain"
        
        return "data_domain"  # Default
    
    # Main workflow with all subgraphs including orchestrator
    workflow = StateGraph(MessagesState)
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("data_domain", create_data_subgraph())
    workflow.add_node("security_domain", create_security_subgraph())
    workflow.add_node("performance_domain", create_performance_subgraph())
    workflow.add_node("compliance_domain", create_compliance_subgraph())
    workflow.add_node("learning_domain", create_learning_subgraph())
    workflow.add_node("orchestrator_domain", create_orchestrator_subgraph())
    
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_to_subgraph,
        {
            "data_domain": "data_domain",
            "security_domain": "security_domain", 
            "performance_domain": "performance_domain",
            "compliance_domain": "compliance_domain",
            "learning_domain": "learning_domain",
            "orchestrator_domain": "orchestrator_domain"
        }
    )
    
    # All subgraphs end the workflow
    workflow.add_edge("data_domain", END)
    workflow.add_edge("security_domain", END)
    workflow.add_edge("performance_domain", END)
    workflow.add_edge("compliance_domain", END)
    workflow.add_edge("learning_domain", END)
    workflow.add_edge("orchestrator_domain", END)
    
    return workflow.compile()
