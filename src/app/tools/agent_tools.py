import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langchain_core.tools import tool
from app.tools.neo4j_client import Neo4jClient
from app.tools.vector_search import VectorSearchClient
from app.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
import re

@tool
def neo4j_query_tool(question: str) -> str:
    """Execute Cypher queries against Neo4j database for structured data retrieval."""
    
    # Generate Cypher query with explicit instructions
    system_prompt = """You are an expert at generating Cypher queries for Neo4j.
    
    CRITICAL: Return ONLY the raw Cypher query with no formatting, no markdown, no code blocks.
    
    Examples:
    - Question: "Count servers" → Answer: MATCH (s:Server) RETURN COUNT(s) as count
    - Question: "Show 3 nodes" → Answer: MATCH (n) RETURN n LIMIT 3
    
    Generate ONLY the raw Cypher query:"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{question}")
    ])
    
    llm = get_llm()
    cypher_generator = prompt | llm
    response = cypher_generator.invoke({"question": question})
    cypher_query = response.content.strip()
    
    # Clean the query - remove any markdown formatting
    cypher_query = re.sub(r'```\w*\n?', '', cypher_query)
    cypher_query = re.sub(r'\n```', '', cypher_query)
    cypher_query = cypher_query.strip()
    
    print(f"Cleaned Cypher query: {cypher_query}")
    
    # Execute query
    client = Neo4jClient()
    try:
        results = client.execute_cypher(cypher_query)
        if results:
            return f"Found {len(results)} results: {results[:3]}"
        else:
            return f"Query executed successfully but returned no results."
    except Exception as e:
        return f"Query failed: {str(e)}"
    finally:
        client.close()

@tool
def vector_search_tool(question: str) -> str:
    """Perform semantic vector search to find related nodes and content."""
    
    try:
        client = VectorSearchClient()
        results = client.similarity_search(question, k=3)  # Reduced to 3 for faster response
        
        if results:
            formatted_results = []
            for node_id, metadata in results:
                labels = metadata.get('labels', 'Unknown')
                props = {k: v for k, v in metadata.items() if k.startswith('prop_')}
                formatted_results.append(f"{labels}: {props}")
            
            return f"Found {len(results)} relevant nodes: {'; '.join(formatted_results)}"
        else:
            return f"No relevant nodes found for: {question}"
            
    except Exception as e:
        return f"Vector search failed: {str(e)}"
