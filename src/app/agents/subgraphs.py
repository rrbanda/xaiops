import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from app.llm_config import get_llm  # Add this import
from app.agents.specialists import (
    create_graph_agent, create_vector_agent, create_security_agent,
    create_performance_agent, create_compliance_agent
)

def create_data_subgraph():
    """Subgraph for data retrieval and analysis."""
    workflow = StateGraph(MessagesState)
    
    workflow.add_node("graph_agent", create_graph_agent())
    workflow.add_node("vector_agent", create_vector_agent())
    
    workflow.add_edge(START, "graph_agent")
    workflow.add_edge("graph_agent", "vector_agent")
    workflow.add_edge("vector_agent", END)
    
    return workflow.compile()

def create_security_subgraph():
    """Subgraph for security analysis."""
    workflow = StateGraph(MessagesState)
    
    workflow.add_node("security_agent", create_security_agent())
    
    workflow.add_edge(START, "security_agent")
    workflow.add_edge("security_agent", END)
    
    return workflow.compile()

def create_performance_subgraph():
    """Subgraph for performance analysis."""
    workflow = StateGraph(MessagesState)
    
    workflow.add_node("performance_agent", create_performance_agent())
    
    workflow.add_edge(START, "performance_agent")
    workflow.add_edge("performance_agent", END)
    
    return workflow.compile()

def create_compliance_subgraph():
    """Subgraph for compliance analysis."""
    workflow = StateGraph(MessagesState)
    
    workflow.add_node("compliance_agent", create_compliance_agent())
    
    workflow.add_edge(START, "compliance_agent") 
    workflow.add_edge("compliance_agent", END)
    
    return workflow.compile()

def create_learning_subgraph():
    """Subgraph for autonomous learning and knowledge updates."""
    
    @tool
    def propose_knowledge_update(entity: str, relationship: str, confidence: float) -> str:
        """Propose a knowledge graph update for validation."""
        if confidence > 0.8:
            return f"HIGH CONFIDENCE: Update {entity} -> {relationship}"
        else:
            return f"LOW CONFIDENCE: Needs review - {entity} -> {relationship}"
    
    @tool
    def extract_learning_pattern(domain: str, pattern: str, frequency: int) -> str:
        """Extract reusable patterns from agent interactions."""
        return f"Pattern learned in {domain}: {pattern} (seen {frequency} times)"
    
    learning_agent = create_react_agent(
        model=get_llm(),  # Now properly imported
        tools=[propose_knowledge_update, extract_learning_pattern],
        prompt=(
            "You analyze multi-agent conversations to identify learning opportunities:\n"
            "1. New infrastructure entities or relationships discovered\n"
            "2. Recurring patterns in security/performance issues\n"
            "3. Successful problem-solving approaches\n"
            "Only propose high-confidence updates (>0.8) to prevent knowledge contamination.\n"
            "Focus on actionable insights that improve future responses."
        ),
        name="learning_agent"
    )
    
    workflow = StateGraph(MessagesState)
    workflow.add_node("learning_agent", learning_agent)
    workflow.add_edge(START, "learning_agent")
    workflow.add_edge("learning_agent", END)
    
    return workflow.compile()

def create_orchestrator_subgraph():
    """Subgraph that coordinates multiple domains for cross-domain analysis."""
    
    @tool
    def invoke_security_analysis(query: str) -> str:
        """Trigger security domain analysis and return findings."""
        # In real implementation, this would call security subgraph
        return f"Security analysis for: {query} - Found potential vulnerabilities in web servers"
    
    @tool
    def invoke_performance_analysis(query: str) -> str:
        """Trigger performance domain analysis and return findings."""
        # In real implementation, this would call performance subgraph
        return f"Performance analysis for: {query} - Detected high CPU usage on affected servers"
    
    @tool
    def invoke_compliance_analysis(query: str) -> str:
        """Trigger compliance domain analysis and return findings."""
        # In real implementation, this would call compliance subgraph
        return f"Compliance analysis for: {query} - Policy violations detected"
    
    @tool
    def synthesize_cross_domain_insights(primary_finding: str, secondary_findings: str) -> str:
        """Combine insights from multiple domains into unified recommendations."""
        return f"Cross-domain synthesis: Primary issue ({primary_finding}) has implications: {secondary_findings}"
    
    orchestrator_agent = create_react_agent(
        model=get_llm(),
        tools=[
            invoke_security_analysis, invoke_performance_analysis,
            invoke_compliance_analysis, synthesize_cross_domain_insights
        ],
        prompt=(
            "You are a cross-domain orchestrator that analyzes infrastructure issues holistically.\n\n"
            "When investigating problems:\n"
            "1. Start with the primary domain based on the query\n"
            "2. Identify potential impacts on other domains\n"
            "3. Invoke relevant domain analyses to gather comprehensive data\n"
            "4. Synthesize findings into unified recommendations\n\n"
            "Example: Security vulnerability → check performance impact → verify compliance implications\n"
            "Focus on root causes and cascading effects across domains."
        ),
        name="orchestrator_agent"
    )
    
    workflow = StateGraph(MessagesState)
    workflow.add_node("orchestrator_agent", orchestrator_agent)
    workflow.add_edge(START, "orchestrator_agent")
    workflow.add_edge("orchestrator_agent", END)
    
    return workflow.compile()
