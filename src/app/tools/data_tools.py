import os
from langchain_core.tools import tool
from neo4j import GraphDatabase
from typing import Dict, Any, List

class Neo4jQueryTool:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        self.driver = None
    
    def connect(self):
        if not self.driver:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query: str, parameters: Dict = None) -> List[Dict[str, Any]]:
        self.connect()
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            return [{"error": str(e)}]

# Global instance
_neo4j_client = Neo4jQueryTool()

@tool
def neo4j_query_tool(query_type: str, search_term: str = "", limit: int = 10) -> str:
    """
    Execute Neo4j queries optimized for AI-generated knowledge graph schema.
    
    Query types:
    - "systems": Find systems/servers
    - "services": Find services and dependencies  
    - "vulnerabilities": Find security vulnerabilities
    - "events": Find events and incidents
    - "dependencies": Show service dependencies
    - "overview": Get infrastructure overview
    - "search": Search by keyword across all entities
    - "cypher": Execute custom Cypher query (use search_term as query)
    """
    
    try:
        if query_type == "systems":
            query = """
            MATCH (n)
            WHERE any(label in labels(n) WHERE label IN ['System', 'Server'])
            RETURN n.name as name, labels(n) as types, 
                   n.environment as environment, 
                   n.system_id as system_id,
                   properties(n) as properties
            ORDER BY n.name
            LIMIT $limit
            """
            params = {"limit": limit}
            
        elif query_type == "services":
            query = """
            MATCH (s:Service)
            OPTIONAL MATCH (s)-[r]->(related)
            RETURN s.name as service, s.status as status,
                   collect({relationship: type(r), target: related.name, target_type: labels(related)}) as connections
            ORDER BY s.name
            LIMIT $limit
            """
            params = {"limit": limit}
            
        elif query_type == "vulnerabilities":
            query = """
            MATCH (v)
            WHERE any(label in labels(v) WHERE label IN ['Vulnerability', 'CVE', 'Security'])
            OPTIONAL MATCH (v)-[r:AFFECTS|IMPACTS]->(affected)
            RETURN v.name as vulnerability, v.severity as severity,
                   collect({affected_entity: affected.name, affected_type: labels(affected)}) as impacts
            ORDER BY v.severity DESC, v.name
            LIMIT $limit
            """
            params = {"limit": limit}
            
        elif query_type == "events":
            query = """
            MATCH (e)
            WHERE any(label in labels(e) WHERE label IN ['Event', 'Incident', 'Alert', 'Log'])
            RETURN e.title as event, e.severity as severity, 
                   e.timestamp as timestamp, e.system_id as system,
                   e.event_type as type, e.description as description
            ORDER BY e.timestamp DESC
            LIMIT $limit
            """
            params = {"limit": limit}
            
        elif query_type == "dependencies":
            query = """
            MATCH (source)-[r:DEPENDS_ON|USES|REQUIRES]->(target)
            WHERE any(label in labels(source) WHERE label IN ['Service', 'Application', 'Component'])
            RETURN source.name as from_entity, labels(source) as from_type,
                   type(r) as relationship, 
                   target.name as to_entity, labels(target) as to_type
            ORDER BY source.name
            LIMIT $limit
            """
            params = {"limit": limit}
            
        elif query_type == "overview":
            query = """
            CALL {
                MATCH (n) 
                RETURN labels(n)[0] as entity_type, count(n) as count
                ORDER BY count DESC
            }
            RETURN entity_type, count
            LIMIT 10
            """
            params = {}
            
        elif query_type == "search":
            if not search_term:
                return "Error: search_term required for search query type"
            
            query = """
            MATCH (n)
            WHERE any(prop in keys(n) WHERE toString(n[prop]) =~ $pattern)
            RETURN labels(n)[0] as entity_type, n.name as name,
                   n.system_id as system_id, properties(n) as properties
            ORDER BY n.name
            LIMIT $limit
            """
            params = {"pattern": f"(?i).*{search_term}.*", "limit": limit}
            
        elif query_type == "cypher":
            if not search_term:
                return "Error: Cypher query required in search_term parameter"
            query = search_term
            params = {"limit": limit}
            
        else:
            return f"Error: Unknown query_type '{query_type}'. Available types: systems, services, vulnerabilities, events, dependencies, overview, search, cypher"
        
        # Execute query
        results = _neo4j_client.execute_query(query, params)
        
        if not results:
            return f"No results found for query type: {query_type}"
        
        # Format results for agent consumption
        if len(results) == 1 and "error" in results[0]:
            return f"Query error: {results[0]['error']}"
        
        # Format based on query type
        if query_type == "overview":
            formatted = "Infrastructure Overview:\n"
            for record in results:
                formatted += f"• {record.get('entity_type', 'Unknown')}: {record.get('count', 0)} entities\n"
        else:
            formatted = f"Results for {query_type} (showing {len(results)} items):\n"
            for i, record in enumerate(results, 1):
                formatted += f"{i}. "
                for key, value in record.items():
                    if value is not None:
                        formatted += f"{key}: {value}, "
                formatted = formatted.rstrip(", ") + "\n"
        
        return formatted
        
    except Exception as e:
        return f"Neo4j query error: {str(e)}"

@tool  
def vector_search_tool(query: str, top_k: int = 5) -> str:
    """
    Execute vector similarity search across infrastructure data.
    
    Args:
        query: Search query for semantic similarity
        top_k: Number of top results to return
    
    Returns:
        Formatted string with similar infrastructure entities
    """
    try:
        from app.tools.vector_search import VectorSearchClient
        
        client = VectorSearchClient()
        results = client.similarity_search(query, k=top_k)
        
        if not results:
            return f"No similar items found for: {query}"
        
        formatted = f"Vector similarity results for '{query}' (top {len(results)}):\n"
        for i, (node_id, metadata) in enumerate(results, 1):
            labels = metadata.get('labels', 'Unknown')
            # Extract property values for display
            props = {}
            for key, value in metadata.items():
                if key.startswith('prop_') and value:
                    clean_key = key.replace('prop_', '')
                    props[clean_key] = value
            
            formatted += f"{i}. {labels}: {props}\n"
        
        return formatted
        
    except Exception as e:
        return f"Vector search error: {str(e)}"
