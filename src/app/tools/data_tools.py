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

# Global vector search client instance (lazy initialization)
_vector_client = None

def get_vector_client():
    """Get or create the global vector search client."""
    global _vector_client
    if _vector_client is None:
        from app.tools.vector_search import VectorSearchClient
        _vector_client = VectorSearchClient(lazy_init=True)
    return _vector_client

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
    
    Enhanced GraphRAG query types:
    - "system_neighbors": Find direct neighbors of a specific system
    - "vulnerability_impact": Enhanced vulnerability impact analysis
    - "service_health": Service status with dependency context
    - "incident_correlation": Find incidents related to a system/service
    - "dependency_path": Trace dependency paths between systems
    - "system_context": Rich contextual information about a system
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
            
        # Enhanced GraphRAG query types (safe, bounded, predefined)
        # All new query types include: input validation, result limits, parameterized queries,
        # bounded traversal depths, and protection against expensive operations
        elif query_type == "system_neighbors":
            if not search_term:
                return "Error: system_name required for system_neighbors query"
            query = """
            MATCH (system)
            WHERE system.name = $system_name OR 
                  any(prop in keys(system) WHERE toString(system[prop]) = $system_name)
            OPTIONAL MATCH (system)-[r]-(neighbor)
            WHERE neighbor IS NOT NULL
            RETURN system.name as system_name,
                   labels(system) as system_type,
                   collect(DISTINCT {
                       neighbor_name: neighbor.name,
                       neighbor_type: labels(neighbor)[0],
                       relationship: type(r)
                   })[0..$limit] as neighbors
            LIMIT 1
            """
            params = {"system_name": search_term, "limit": limit}
            
        elif query_type == "vulnerability_impact":
            query = """
            MATCH (v)
            WHERE any(label in labels(v) WHERE label IN ['Vulnerability', 'CVE', 'Security'])
            AND ($search_term = '' OR v.name CONTAINS $search_term OR 
                 toString(v.severity) CONTAINS $search_term)
            OPTIONAL MATCH (v)-[r]-(affected)
            RETURN v.name as vulnerability,
                   v.severity as severity,
                   v.description as description,
                   collect(DISTINCT {
                       affected_entity: affected.name,
                       affected_type: labels(affected)[0],
                       relationship: type(r)
                   })[0..$limit] as impact_analysis
            ORDER BY v.severity DESC, v.name
            LIMIT $limit
            """
            params = {"search_term": search_term, "limit": limit}
            
        elif query_type == "service_health":
            if not search_term:
                return "Error: service_name required for service_health query"
            query = """
            MATCH (s:Service)
            WHERE s.name = $service_name OR s.name CONTAINS $service_name
            OPTIONAL MATCH (s)-[dep:DEPENDS_ON]->(dependency)
            OPTIONAL MATCH (s)<-[used:USES]-(dependent)
            RETURN s.name as service_name,
                   s.status as current_status,
                   s.health_check_url as health_url,
                   collect(DISTINCT {
                       dependency: dependency.name,
                       dependency_type: labels(dependency)[0]
                   })[0..10] as dependencies,
                   collect(DISTINCT {
                       dependent: dependent.name,
                       dependent_type: labels(dependent)[0]
                   })[0..10] as dependents
            ORDER BY s.name
            LIMIT $limit
            """
            params = {"service_name": search_term, "limit": limit}
            
        elif query_type == "incident_correlation":
            if not search_term:
                return "Error: system/service name required for incident_correlation query"
            query = """
            MATCH (entity)
            WHERE entity.name = $entity_name OR entity.name CONTAINS $entity_name
            OPTIONAL MATCH (entity)-[r]-(incident)
            WHERE any(label in labels(incident) WHERE label IN ['Incident', 'ServiceNowIncident', 'Event'])
            RETURN entity.name as entity_name,
                   labels(entity) as entity_type,
                   collect(DISTINCT {
                       incident_id: incident.number,
                       incident_summary: incident.short_description,
                       incident_state: incident.state,
                       incident_severity: incident.severity,
                       relationship: type(r)
                   })[0..$limit] as related_incidents
            ORDER BY entity.name
            LIMIT $limit
            """
            params = {"entity_name": search_term, "limit": limit}
            
        elif query_type == "dependency_path":
            if not search_term:
                return "Error: 'source,target' required for dependency_path query (comma-separated)"
            
            parts = search_term.split(',')
            if len(parts) != 2:
                return "Error: dependency_path requires 'source,target' format"
            
            source_name = parts[0].strip()
            target_name = parts[1].strip()
            
            query = """
            MATCH (source), (target)
            WHERE (source.name = $source_name OR source.name CONTAINS $source_name)
              AND (target.name = $target_name OR target.name CONTAINS $target_name)
            OPTIONAL MATCH path = shortestPath((source)-[:DEPENDS_ON|USES|REQUIRES*1..5]->(target))
            RETURN source.name as source_system,
                   target.name as target_system,
                   CASE WHEN path IS NOT NULL 
                        THEN [node in nodes(path) | node.name] 
                        ELSE [] END as dependency_path,
                   CASE WHEN path IS NOT NULL 
                        THEN [rel in relationships(path) | type(rel)] 
                        ELSE [] END as relationship_types,
                   CASE WHEN path IS NOT NULL 
                        THEN length(path) 
                        ELSE -1 END as path_length
            LIMIT 1
            """
            params = {"source_name": source_name, "target_name": target_name}
            
        elif query_type == "system_context":
            if not search_term:
                return "Error: system_name required for system_context query"
            query = """
            MATCH (system)
            WHERE system.name = $system_name OR 
                  any(prop in keys(system) WHERE toString(system[prop]) CONTAINS $system_name)
            OPTIONAL MATCH (system)-[r1]-(direct_neighbor)
            OPTIONAL MATCH (system)-[*2..2]-(second_degree)
            WHERE second_degree <> system AND second_degree <> direct_neighbor
            RETURN system.name as system_name,
                   labels(system) as system_types,
                   properties(system) as system_properties,
                   collect(DISTINCT {
                       neighbor: direct_neighbor.name,
                       neighbor_type: labels(direct_neighbor)[0],
                       relationship: type(r1),
                       neighbor_properties: properties(direct_neighbor)
                   })[0..10] as direct_context,
                   collect(DISTINCT second_degree.name)[0..5] as extended_context
            ORDER BY system.name
            LIMIT $limit
            """
            params = {"system_name": search_term, "limit": limit}
            
        else:
            available_types = "systems, services, vulnerabilities, events, dependencies, overview, search, cypher, system_neighbors, vulnerability_impact, service_health, incident_correlation, dependency_path, system_context"
            return f"Error: Unknown query_type '{query_type}'. Available types: {available_types}"
        
        # Execute query
        results = _neo4j_client.execute_query(query, params)
        
        if not results:
            return f"No results found for query type: {query_type}"
        
        # Format results for agent consumption
        if len(results) == 1 and "error" in results[0]:
            return f"Query error: {results[0]['error']}"
        
        # Enhanced formatting for GraphRAG query types
        if query_type == "overview":
            formatted = "Infrastructure Overview:\n"
            for record in results:
                formatted += f"• {record.get('entity_type', 'Unknown')}: {record.get('count', 0)} entities\n"
                
        elif query_type == "system_neighbors":
            formatted = f"System Neighborhood Analysis (showing {len(results)} systems):\n"
            for record in results:
                formatted += f"System: {record.get('system_name', 'Unknown')}\n"
                formatted += f"Type: {record.get('system_type', 'Unknown')}\n"
                neighbors = record.get('neighbors', [])
                if neighbors and neighbors != [None]:
                    formatted += f"Connected to {len(neighbors)} neighbors:\n"
                    for neighbor in neighbors[:10]:  # Limit display
                        if neighbor and neighbor.get('neighbor_name'):
                            formatted += f"  • {neighbor['neighbor_name']} ({neighbor.get('neighbor_type', 'Unknown')}) via {neighbor.get('relationship', 'Unknown')}\n"
                else:
                    formatted += "  • No direct neighbors found\n"
                formatted += "\n"
                
        elif query_type == "vulnerability_impact":
            formatted = f"Vulnerability Impact Analysis (showing {len(results)} vulnerabilities):\n"
            for record in results:
                formatted += f"Vulnerability: {record.get('vulnerability', 'Unknown')}\n"
                formatted += f"Severity: {record.get('severity', 'Unknown')}\n"
                if record.get('description'):
                    formatted += f"Description: {record['description']}\n"
                impacts = record.get('impact_analysis', [])
                if impacts and impacts != [None]:
                    formatted += f"Affects {len(impacts)} entities:\n"
                    for impact in impacts[:5]:  # Limit display
                        if impact and impact.get('affected_entity'):
                            formatted += f"  • {impact['affected_entity']} ({impact.get('affected_type', 'Unknown')})\n"
                else:
                    formatted += "  • No affected entities found\n"
                formatted += "\n"
                
        elif query_type == "service_health":
            formatted = f"Service Health Analysis (showing {len(results)} services):\n"
            for record in results:
                formatted += f"Service: {record.get('service_name', 'Unknown')}\n"
                formatted += f"Status: {record.get('current_status', 'Unknown')}\n"
                if record.get('health_url'):
                    formatted += f"Health Check: {record['health_url']}\n"
                
                deps = record.get('dependencies', [])
                if deps and deps != [None]:
                    formatted += f"Dependencies ({len(deps)}):\n"
                    for dep in deps[:5]:
                        if dep and dep.get('dependency'):
                            formatted += f"  • {dep['dependency']} ({dep.get('dependency_type', 'Unknown')})\n"
                
                dependents = record.get('dependents', [])
                if dependents and dependents != [None]:
                    formatted += f"Dependents ({len(dependents)}):\n"
                    for dependent in dependents[:5]:
                        if dependent and dependent.get('dependent'):
                            formatted += f"  • {dependent['dependent']} ({dependent.get('dependent_type', 'Unknown')})\n"
                formatted += "\n"
                
        elif query_type == "incident_correlation":
            formatted = f"Incident Correlation Analysis (showing {len(results)} entities):\n"
            for record in results:
                formatted += f"Entity: {record.get('entity_name', 'Unknown')}\n"
                formatted += f"Type: {record.get('entity_type', 'Unknown')}\n"
                incidents = record.get('related_incidents', [])
                if incidents and incidents != [None]:
                    formatted += f"Related Incidents ({len(incidents)}):\n"
                    for incident in incidents[:5]:
                        if incident and incident.get('incident_id'):
                            formatted += f"  • {incident['incident_id']}: {incident.get('incident_summary', 'No summary')}\n"
                            formatted += f"    State: {incident.get('incident_state', 'Unknown')}, Severity: {incident.get('incident_severity', 'Unknown')}\n"
                else:
                    formatted += "  • No related incidents found\n"
                formatted += "\n"
                
        elif query_type == "dependency_path":
            formatted = f"Dependency Path Analysis (showing {len(results)} paths):\n"
            for record in results:
                source = record.get('source_system', 'Unknown')
                target = record.get('target_system', 'Unknown')
                path_length = record.get('path_length', -1)
                
                if path_length > 0:
                    path = record.get('dependency_path', [])
                    rel_types = record.get('relationship_types', [])
                    formatted += f"Path from {source} to {target} (length: {path_length}):\n"
                    
                    if path and len(path) > 1:
                        for i in range(len(path) - 1):
                            current = path[i]
                            next_node = path[i + 1]
                            rel_type = rel_types[i] if i < len(rel_types) else "UNKNOWN"
                            formatted += f"  {current} --{rel_type}--> {next_node}\n"
                    else:
                        formatted += f"  Direct path found\n"
                else:
                    formatted += f"No dependency path found between {source} and {target}\n"
                formatted += "\n"
                
        elif query_type == "system_context":
            formatted = f"System Context Analysis (showing {len(results)} systems):\n"
            for record in results:
                formatted += f"System: {record.get('system_name', 'Unknown')}\n"
                formatted += f"Types: {record.get('system_types', 'Unknown')}\n"
                
                props = record.get('system_properties', {})
                if props:
                    formatted += f"Properties: {', '.join([f'{k}={v}' for k, v in list(props.items())[:5]])}\n"
                
                direct_ctx = record.get('direct_context', [])
                if direct_ctx and direct_ctx != [None]:
                    formatted += f"Direct Context ({len(direct_ctx)} connections):\n"
                    for ctx in direct_ctx[:8]:
                        if ctx and ctx.get('neighbor'):
                            formatted += f"  • {ctx['neighbor']} ({ctx.get('neighbor_type', 'Unknown')}) via {ctx.get('relationship', 'Unknown')}\n"
                
                extended_ctx = record.get('extended_context', [])
                if extended_ctx and extended_ctx != [None] and extended_ctx != []:
                    clean_extended = [item for item in extended_ctx if item]
                    if clean_extended:
                        formatted += f"Extended Context: {', '.join(clean_extended[:5])}\n"
                formatted += "\n"
                
        else:
            # Default formatting for existing query types
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
        # Use global client instance - data only loaded once on first use
        client = get_vector_client()
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
