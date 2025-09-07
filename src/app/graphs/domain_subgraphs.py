import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from app.llm_config import get_llm
from app.tools.hitl_tools import security_approval_gate
from app.tools.data_tools import neo4j_query_tool, vector_search_tool
from app.prompts import load_prompt

def extract_user_query(state):
    """Helper function to safely extract user query from state."""
    first_message = state["messages"][0]
    
    if isinstance(first_message, dict):
        content = first_message.get("content", "")
    else:
        content = getattr(first_message, 'content', "")
    
    # Handle case where content might be a list
    if isinstance(content, list):
        content = " ".join(str(item) for item in content)
    elif not isinstance(content, str):
        content = str(content)
    
    return content

def create_data_subgraph():
    """Fixed data subgraph with specialized agent roles."""
    
    def graph_collector_node(state):
        """PRIMARY data collection using Neo4j - gets the main data."""
        original_query = extract_user_query(state)
        
        # Determine appropriate query type from user question
        query_type = "overview"
        search_term = ""
        
        query_lower = original_query.lower()
        if any(word in query_lower for word in ["server", "system", "machine"]):
            query_type = "systems"
        elif any(word in query_lower for word in ["service", "application", "app"]):
            query_type = "services"
        elif any(word in query_lower for word in ["vulnerability", "security", "cve"]):
            query_type = "vulnerabilities"
        elif any(word in query_lower for word in ["event", "incident", "alert"]):
            query_type = "events"
        elif any(word in query_lower for word in ["dependency", "depend", "connection"]):
            query_type = "dependencies"
        elif "search" in query_lower:
            query_type = "search"
            words = original_query.split()
            if len(words) > 1:
                search_term = words[-1]
        
        # Create context for graph agent using direct tool parameters
        graph_context = {
            "messages": [{"role": "user", "content": f"Use neo4j_query_tool with query_type='{query_type}' and search_term='{search_term}' and limit=20"}]
        }
        
        # Create agent that uses Neo4j tool
        graph_agent = create_react_agent(
            model=get_llm(),
            tools=[neo4j_query_tool],
            prompt=(
                "You are a database expert. Use the neo4j_query_tool to get structured infrastructure data.\n"
                "Call the tool with the exact parameters specified in the user message.\n"
                "Return clean, factual data from the database without commentary."
            ),
            name="graph_collector",
        )
        
        graph_result = graph_agent.invoke(graph_context)
        graph_findings = graph_result["messages"][-1].content
        
        return {
            "messages": [
                {"role": "assistant", "content": graph_findings, "name": "graph_collector"}
            ]
        }
    
    def context_enhancer_node(state):
        """SECONDARY enhancement using vector search - adds context and patterns."""
        original_query = extract_user_query(state)
        
        # Extract key terms for semantic search
        query_lower = original_query.lower()
        
        if "server" in query_lower:
            search_query = "web server production"
        elif "security" in query_lower:
            search_query = "security vulnerability"
        elif "service" in query_lower:
            search_query = "service monitoring"
        else:
            # Use main concepts from query
            important_words = [word for word in original_query.split() 
                             if len(word) > 3 and word.lower() not in ['show', 'find', 'get', 'list', 'all']]
            search_query = " ".join(important_words[:2]) if important_words else "infrastructure"
        
        # Create context for vector search
        vector_context = {
            "messages": [{"role": "user", "content": f"Use vector_search_tool to find patterns related to: {search_query}"}]
        }
        
        # Create agent that uses vector search
        vector_agent = create_react_agent(
            model=get_llm(),
            tools=[vector_search_tool],
            prompt=(
                "You are a pattern recognition expert. Use vector_search_tool to find related infrastructure patterns.\n"
                "Focus on finding similar configurations, related systems, or contextual information.\n"
                "Provide insights about patterns and relationships found in the search results."
            ),
            name="context_enhancer",
        )
        
        vector_result = vector_agent.invoke(vector_context)
        vector_findings = vector_result["messages"][-1].content
        
        return {
            "messages": [
                {"role": "assistant", "content": vector_findings, "name": "context_enhancer"}
            ]
        }
    
    def synthesis_node(state):
        """Combine structured data with contextual insights."""
        original_query = extract_user_query(state)
        
        # Extract findings from both collectors
        graph_data = ""
        context_data = ""
        
        for msg in state["messages"]:
            if hasattr(msg, 'name') or (isinstance(msg, dict) and 'name' in msg):
                name = msg.get('name') if isinstance(msg, dict) else getattr(msg, 'name', None)
                content = msg.get('content') if isinstance(msg, dict) else getattr(msg, 'content', '')
                
                if name == "graph_collector":
                    graph_data = content
                elif name == "context_enhancer":
                    context_data = content
        
        # Create synthesis prompt
        synthesis_prompt = f"""
        User asked: "{original_query}"
        
        PRIMARY DATA (from database):
        {graph_data}
        
        CONTEXTUAL INSIGHTS (from pattern analysis):
        {context_data}
        
        Create a comprehensive response that:
        1. Directly answers the user's question using the primary data
        2. Adds relevant context and insights where helpful
        3. Uses clear formatting with bullet points for lists
        4. Provides a brief summary
        
        Focus on being helpful and informative while avoiding redundancy.
        """
        
        llm = get_llm()
        response = llm.invoke(synthesis_prompt)
        
        return {
            "messages": [
                {"role": "assistant", "content": response.content}
            ]
        }
    
    # Build workflow: Primary data → Context enhancement → Synthesis
    workflow = StateGraph(MessagesState)
    workflow.add_node("graph_collector", graph_collector_node)
    workflow.add_node("context_enhancer", context_enhancer_node)
    workflow.add_node("synthesis", synthesis_node)
    
    workflow.add_edge(START, "graph_collector")
    workflow.add_edge("graph_collector", "context_enhancer")
    workflow.add_edge("context_enhancer", "synthesis")
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()

def create_security_subgraph():
    """Security subgraph with external prompt."""
    workflow = StateGraph(MessagesState)
    
    security_agent = create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool, vector_search_tool, security_approval_gate],
        prompt=load_prompt("security_domain"),
        name="security_agent",
    )
    
    workflow.add_node("security_agent", security_agent)
    workflow.add_edge(START, "security_agent")
    workflow.add_edge("security_agent", END)
    
    return workflow.compile()

def create_performance_subgraph():
    """Performance subgraph with external prompt."""
    workflow = StateGraph(MessagesState)
    
    performance_agent = create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool, vector_search_tool, security_approval_gate],
        prompt=load_prompt("performance_domain"),
        name="performance_agent",
    )
    
    workflow.add_node("performance_agent", performance_agent)
    workflow.add_edge(START, "performance_agent")
    workflow.add_edge("performance_agent", END)
    
    return workflow.compile()

def create_compliance_subgraph():
    """Compliance subgraph with external prompt."""
    workflow = StateGraph(MessagesState)
    
    compliance_agent = create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool, vector_search_tool, security_approval_gate],
        prompt=load_prompt("compliance_domain"),
        name="compliance_agent",
    )
    
    workflow.add_node("compliance_agent", compliance_agent)
    workflow.add_edge(START, "compliance_agent")
    workflow.add_edge("compliance_agent", END)
    
    return workflow.compile()

def create_learning_subgraph():
    """Learning subgraph with external prompt."""
    
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
        model=get_llm(),
        tools=[propose_knowledge_update, extract_learning_pattern],
        prompt=load_prompt("learning_domain"),
        name="learning_agent"
    )
    
    workflow = StateGraph(MessagesState)
    workflow.add_node("learning_agent", learning_agent)
    workflow.add_edge(START, "learning_agent")
    workflow.add_edge("learning_agent", END)
    
    return workflow.compile()
