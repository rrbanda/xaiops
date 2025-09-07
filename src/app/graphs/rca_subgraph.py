import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import create_react_agent
from app.llm_config import get_llm
from app.prompts import load_prompt
from app.tools.rca_tools import (
    discover_incidents,
    rca_timeline_query, 
    dependency_traversal_query, 
    similarity_search_analysis
)
from app.tools.data_tools import neo4j_query_tool, vector_search_tool

def create_rca_subgraph():
    """Pure agentic RCA subgraph - agent decides investigation approach autonomously."""
    workflow = StateGraph(MessagesState)
    
    rca_agent = create_react_agent(
        model=get_llm(),
        tools=[
            discover_incidents,
            rca_timeline_query, 
            dependency_traversal_query, 
            similarity_search_analysis,
            neo4j_query_tool,
            vector_search_tool
        ],
        prompt=load_prompt("rca_domain"),
        name="rca_agent",
    )
    
    workflow.add_node("rca_agent", rca_agent)
    workflow.add_edge(START, "rca_agent") 
    workflow.add_edge("rca_agent", END)
    
    return workflow.compile()
