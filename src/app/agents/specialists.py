import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.prebuilt import create_react_agent
from app.llm_config import get_llm
from app.tools.agent_tools import neo4j_query_tool, vector_search_tool

# Create agents with recursion limit and better prompts
def create_graph_agent():
    return create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool],
        prompt=(
            "You are a graph database expert. Use the neo4j_query_tool to answer questions.\n"
            "After getting results from the tool, provide a clear answer and STOP.\n"
            "Do NOT call the tool multiple times for the same question."
        ),
        name="graph_agent",
    )

def create_vector_agent():
    return create_react_agent(
        model=get_llm(),
        tools=[vector_search_tool],
        prompt=(
            "You are a semantic search expert. Use the vector_search_tool to find related content.\n"
            "After getting results from the tool, provide a clear answer and STOP.\n"
            "Do NOT call the tool multiple times for the same question."
        ),
        name="vector_agent",
    )
