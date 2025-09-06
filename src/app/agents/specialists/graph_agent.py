from langgraph.prebuilt import create_react_agent
from app.llm_config import get_llm
from app.tools.agent_tools import neo4j_query_tool

def create_graph_agent():
    """Create specialized graph database agent."""
    return create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool],
        prompt="You are a graph database expert...",
        name="graph_agent",
    )
