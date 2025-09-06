import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from app.llm_config import get_llm
from app.tools.hitl_tools import security_approval_gate
from app.tools.agent_tools import neo4j_query_tool, vector_search_tool

def create_data_subgraph():
   """Fixed data subgraph with proper state management and user-facing output."""
   
   def graph_collector_node(state):
       """Collect structured data using graph queries."""
       # Handle both dict and Message object formats
       first_message = state["messages"][0]
       if isinstance(first_message, dict):
           original_query = first_message["content"]
       else:
           original_query = first_message.content
       
       # Create a clean context for graph agent
       graph_context = {
           "messages": [{"role": "user", "content": f"Use graph database to find: {original_query}"}]
       }
       
       # Create graph agent
       graph_agent = create_react_agent(
           model=get_llm(),
           tools=[neo4j_query_tool],
           prompt=(
               "You are a graph database expert. Use Neo4j queries to find structured data.\n"
               "Focus on relationships, counts, and specific entity lookups.\n"
               "Provide clear, factual results from your queries."
           ),
           name="graph_collector",
       )
       
       graph_result = graph_agent.invoke(graph_context)
       graph_findings = graph_result["messages"][-1].content
       
       # Add findings to state without full conversation
       return {
           "messages": [
               {"role": "assistant", "content": f"Graph findings: {graph_findings}", "name": "graph_collector"}
           ]
       }
   
   def vector_collector_node(state):
       """Collect semantic similarity data."""
       # Handle both dict and Message object formats
       first_message = state["messages"][0]
       if isinstance(first_message, dict):
           original_query = first_message["content"]
       else:
           original_query = first_message.content
       
       # Create clean context for vector agent
       vector_context = {
           "messages": [{"role": "user", "content": f"Use semantic search to find similar items for: {original_query}"}]
       }
       
       # Create vector agent
       vector_agent = create_react_agent(
           model=get_llm(),
           tools=[vector_search_tool],
           prompt=(
               "You are a semantic search expert. Use vector similarity to find related content.\n"
               "Focus on patterns, similar configurations, and related entities.\n"
               "Provide context about relationships and similarities."
           ),
           name="vector_collector",
       )
       
       vector_result = vector_agent.invoke(vector_context)
       vector_findings = vector_result["messages"][-1].content
       
       # Add findings to state
       return {
           "messages": [
               {"role": "assistant", "content": f"Vector findings: {vector_findings}", "name": "vector_collector"}
           ]
       }
   
   def user_response_node(state):
       """Create clean user-facing response from internal findings."""
       # Handle both dict and Message object formats
       first_message = state["messages"][0]
       if isinstance(first_message, dict):
           original_query = first_message["content"]
       else:
           original_query = first_message.content
       
       # Extract findings from previous agents
       graph_findings = ""
       vector_findings = ""
       
       for msg in state["messages"]:
           if hasattr(msg, 'name') or (isinstance(msg, dict) and 'name' in msg):
               name = msg.get('name') if isinstance(msg, dict) else getattr(msg, 'name', None)
               content = msg.get('content') if isinstance(msg, dict) else getattr(msg, 'content', '')
               
               if name == "graph_collector":
                   graph_findings = content
               elif name == "vector_collector":
                   vector_findings = content
       
       # Create user-friendly response prompt
       user_response_prompt = f"""
       User asked: "{original_query}"
       
       Internal findings:
       Graph database: {graph_findings}
       Vector search: {vector_findings}
       
       Create a clean, professional response that directly answers the user's question.
       
       Format requirements:
       - Start with a clear answer to their question
       - Use bullet points or simple lists for multiple items
       - Include a brief summary at the end
       - Avoid technical jargon about tools or internal processes
       - Be concise but complete
       - Focus on actionable information
       
       Example good response:
       "**Servers in your infrastructure:**
       • Web-Prod-01 - Production web server
       • Web-Prod-02 - Production web server  
       • Red Hat Enterprise Linux - System server
       
       **Summary:** Found 3 active servers including production web services."
       """
       
       # Use LLM to create user response
       llm = get_llm()
       user_response = llm.invoke(user_response_prompt)
       
       return {
           "messages": [
               {"role": "assistant", "content": user_response.content}
           ]
       }
   
   # Build workflow with user response node
   workflow = StateGraph(MessagesState)
   workflow.add_node("graph_collector", graph_collector_node)
   workflow.add_node("vector_collector", vector_collector_node)
   workflow.add_node("user_response", user_response_node)
   
   workflow.add_edge(START, "graph_collector")
   workflow.add_edge("graph_collector", "vector_collector")
   workflow.add_edge("vector_collector", "user_response")
   workflow.add_edge("user_response", END)
   
   return workflow.compile()

def create_security_subgraph():
   """Security subgraph - already working, keep as is."""
   workflow = StateGraph(MessagesState)
   
   security_agent = create_react_agent(
       model=get_llm(),
       tools=[neo4j_query_tool, vector_search_tool, security_approval_gate],
       prompt=(
           "You are a cybersecurity expert specializing in infrastructure security analysis.\n"
           "Focus on vulnerabilities, access controls, compliance, security configurations.\n"
           "Use graph queries to map security relationships and vector search for similar threats.\n"
           "Provide security recommendations and identify potential risks.\n"
           "Look for patterns like open ports, outdated software, weak configurations.\n\n"
           "IMPORTANT: Provide clean, actionable responses directly to users. Avoid showing internal tool usage."
       ),
       name="security_agent",
   )
   
   workflow.add_node("security_agent", security_agent)
   workflow.add_edge(START, "security_agent")
   workflow.add_edge("security_agent", END)
   
   return workflow.compile()

def create_performance_subgraph():
   """Performance subgraph - already working, keep as is."""
   workflow = StateGraph(MessagesState)
   
   performance_agent = create_react_agent(
       model=get_llm(),
       tools=[neo4j_query_tool, vector_search_tool, security_approval_gate],
       prompt=(
           "You are a performance optimization expert for infrastructure monitoring.\n"
           "Focus on capacity planning, resource utilization, performance bottlenecks.\n"
           "Use graph queries for current metrics and vector search for performance patterns.\n"
           "Provide optimization recommendations and identify resource constraints.\n"
           "Look for CPU, memory, disk, network performance indicators.\n\n"
           "IMPORTANT: Provide clean, actionable responses directly to users. Avoid showing internal tool usage."
       ),
       name="performance_agent",
   )
   
   workflow.add_node("performance_agent", performance_agent)
   workflow.add_edge(START, "performance_agent")
   workflow.add_edge("performance_agent", END)
   
   return workflow.compile()

def create_compliance_subgraph():
   """Compliance subgraph - keep simple single agent."""
   workflow = StateGraph(MessagesState)
   
   compliance_agent = create_react_agent(
       model=get_llm(),
       tools=[neo4j_query_tool, vector_search_tool, security_approval_gate],
       prompt=(
           "You are a compliance and audit expert for infrastructure governance.\n"
           "Focus on regulatory requirements, policy adherence, audit trails.\n"
           "Use graph queries for compliance mapping and vector search for similar violations.\n"
           "Provide compliance status reports and identify policy gaps.\n"
           "Look for GDPR, SOX, HIPAA, PCI-DSS compliance indicators.\n\n"
           "IMPORTANT: Provide clean, actionable responses directly to users. Avoid showing internal tool usage."
       ),
       name="compliance_agent",
   )
   
   workflow.add_node("compliance_agent", compliance_agent)
   workflow.add_edge(START, "compliance_agent")
   workflow.add_edge("compliance_agent", END)
   
   return workflow.compile()

def create_learning_subgraph():
   """Learning subgraph - keep simple single agent."""
   
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
       prompt=(
           "You analyze multi-agent conversations to identify learning opportunities:\n"
           "1. New infrastructure entities or relationships discovered\n"
           "2. Recurring patterns in security/performance issues\n"
           "3. Successful problem-solving approaches\n"
           "Only propose high-confidence updates (>0.8) to prevent knowledge contamination.\n"
           "Focus on actionable insights that improve future responses.\n\n"
           "IMPORTANT: Provide clean, actionable responses directly to users. Avoid showing internal tool usage."
       ),
       name="learning_agent"
   )
   
   workflow = StateGraph(MessagesState)
   workflow.add_node("learning_agent", learning_agent)
   workflow.add_edge(START, "learning_agent")
   workflow.add_edge("learning_agent", END)
   
   return workflow.compile()


