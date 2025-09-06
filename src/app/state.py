from typing import TypedDict, List, Dict, Any, Literal, Optional
from pydantic import BaseModel

class GraphState(TypedDict, total=False):
    """
    Represents the state of the GraphRAG workflow.
    
    Attributes:
        question: Original user question
        documents: Results from graph or vector queries
        article_ids: Node IDs from vector search (for context)
        next: Next node to execute
        subqueries: Decomposed query parts
        query_type: Routing decision
        context: Additional context for prompting
        response: Final generated response
    """
    question: str
    documents: Dict[str, Any]
    article_ids: List[str]
    next: Literal["router", "vector_search", "graph_query", "decomposer", "response_generator", "done"]
    subqueries: List[str]
    query_type: Literal["vector_search", "graph_query"]
    context: str
    response: str

def create_initial_state(question: str) -> GraphState:
    """Create initial state for a new query."""
    return {
        "question": question,
        "documents": {},
        "article_ids": [],
        "next": "router",
        "subqueries": [],
        "context": "",
        "response": ""
    }

# Pydantic models for structured outputs
class RouteDecision(BaseModel):
    """Router decision model."""
    query_type: Literal["vector_search", "graph_query"]
    reasoning: str

class SubQuery(BaseModel):
    """Decomposed query model."""
    sub_query: str
    query_type: Literal["vector", "graph"]
