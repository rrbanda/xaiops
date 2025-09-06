import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.prebuilt import create_react_agent
from app.llm_config import get_llm
from app.tools.agent_tools import neo4j_query_tool, vector_search_tool

def create_graph_agent():
    """Create graph database specialist agent."""
    return create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool],
        prompt=(
            "You are a graph database expert specializing in infrastructure queries.\n"
            "Use Neo4j queries to find structured data about servers, services, and relationships.\n"
            "Generate clean Cypher queries and interpret results clearly.\n"
            "Focus on counts, lists, specific lookups, and relationship traversals."
        ),
        name="graph_agent",
    )

def create_vector_agent():
    """Create vector similarity specialist agent.""" 
    return create_react_agent(
        model=get_llm(),
        tools=[vector_search_tool],
        prompt=(
            "You are a semantic search expert specializing in similarity analysis.\n"
            "Use vector search to find related configurations, patterns, and similar infrastructure.\n"
            "Focus on 'similar to', 'related', 'like', and pattern matching queries.\n"
            "Provide context about why items are similar."
        ),
        name="vector_agent",
    )

def create_security_agent():
    """Create security specialist agent."""
    return create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool, vector_search_tool],
        prompt=(
            "You are a cybersecurity expert specializing in infrastructure security analysis.\n"
            "Focus on vulnerabilities, access controls, compliance, security configurations.\n"
            "Use graph queries to map security relationships and vector search for similar threats.\n"
            "Provide security recommendations and identify potential risks.\n"
            "Look for patterns like open ports, outdated software, weak configurations."
        ),
        name="security_agent",
    )

def create_performance_agent():
    """Create performance specialist agent."""
    return create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool, vector_search_tool],
        prompt=(
            "You are a performance optimization expert for infrastructure monitoring.\n"
            "Focus on capacity planning, resource utilization, performance bottlenecks.\n"
            "Use graph queries for current metrics and vector search for performance patterns.\n"
            "Provide optimization recommendations and identify resource constraints.\n"
            "Look for CPU, memory, disk, network performance indicators."
        ),
        name="performance_agent",
    )

def create_compliance_agent():
    """Create compliance specialist agent."""
    return create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool, vector_search_tool],
        prompt=(
            "You are a compliance and audit expert for infrastructure governance.\n"
            "Focus on regulatory requirements, policy adherence, audit trails.\n"
            "Use graph queries for compliance mapping and vector search for similar violations.\n"
            "Provide compliance status reports and identify policy gaps.\n"
            "Look for GDPR, SOX, HIPAA, PCI-DSS compliance indicators."
        ),
        name="compliance_agent",
    )
