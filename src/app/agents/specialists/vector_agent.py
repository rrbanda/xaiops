from langgraph.prebuilt import create_react_agent
from app.llm_config import get_llm
from app.tools.agent_tools import vector_search_tool

def create_vector_agent():
    """Create specialized vector search agent."""
    return create_react_agent(
        model=get_llm(),
        tools=[vector_search_tool],
        prompt="You are a semantic search expert...",
        name="vector_agent",
    )
