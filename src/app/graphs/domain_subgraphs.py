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
    first_message = state["messages"][-1]
    
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
        """Pure agentic data collection - agent decides query approach autonomously."""
        original_query = extract_user_query(state)
        
        # Create agent that autonomously decides query parameters
        graph_agent = create_react_agent(
            model=get_llm(),
            tools=[neo4j_query_tool],
            prompt=(
                "You are a database expert analyzing infrastructure queries.\n\n"
                "Use neo4j_query_tool to answer the user's question. YOU decide the best approach:\n"
                "- Which query_type fits their intent (systems, services, vulnerabilities, events, dependencies, overview)\n"
                "- What search_term to use (if any)\n"
                "- Appropriate limit for results\n\n"
                "Guidelines:\n"
                "- For questions about servers, nodes, machines, hosts, infrastructure → use 'systems'\n"
                "- For questions about applications, services, processes → use 'services'\n"
                "- For security, vulnerabilities, CVEs → use 'vulnerabilities'\n"
                "- For incidents, alerts, logs → use 'events'\n"
                "- For connections, relationships → use 'dependencies'\n"
                "- For counts ('how many'), provide the count and brief summary\n"
                "- For environment-specific queries (production, staging, dev), include in search_term\n\n"
                "Return clean, factual data from the database."
            ),
            name="graph_collector",
        )
        
        # Let agent decide everything autonomously
        graph_result = graph_agent.invoke({"messages": [{"role": "user", "content": original_query}]})
        graph_findings = graph_result["messages"][-1].content
        
        return {
            "messages": [
                {"role": "assistant", "content": graph_findings, "name": "graph_collector"}
            ]
        }
    
    def context_enhancer_node(state):
        """Pure agentic context enhancement - agent decides search approach autonomously."""
        original_query = extract_user_query(state)
        
        # Create agent that autonomously decides vector search strategy
        vector_agent = create_react_agent(
            model=get_llm(),
            tools=[vector_search_tool],
            prompt=(
                "You are a semantic search expert specializing in pattern recognition and similarity analysis.\n\n"
                "Use vector_search_tool to find patterns and context related to the user's question. "
                "YOU decide the best search strategy:\n"
                "- What search terms to use for finding similar infrastructure patterns\n"
                "- How many results (top_k) to retrieve based on analysis needs\n"
                "- What patterns and relationships to highlight\n\n"
                "Guidelines for effective searches:\n"
                "- For infrastructure questions → search for 'server configuration production environment'\n"
                "- For security questions → search for 'security vulnerability configuration'\n"  
                "- For service questions → search for 'service monitoring application'\n"
                "- For troubleshooting → search for 'incident outage performance issue'\n"
                "- For counts/inventory → search for relevant entity types and environments\n\n"
                "Focus on finding similar configurations, related systems, patterns, and contextual information "
                "that complement the primary data analysis. Provide insights about discovered patterns and relationships."
            ),
            name="context_enhancer",
        )
        
        # Let agent decide search strategy autonomously
        vector_result = vector_agent.invoke({"messages": [{"role": "user", "content": original_query}]})
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
