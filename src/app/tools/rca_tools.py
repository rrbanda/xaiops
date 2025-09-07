import os
from datetime import datetime, timedelta
from langchain_core.tools import tool
from neo4j import GraphDatabase
from typing import Dict, Any, List

class RCAQueryTool:
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
    
    def execute_query(self, query: str, parameters: Dict = None) -> List[Dict[str, Any]]:
        self.connect()
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            return [{"error": str(e)}]

# Global RCA client instance
_rca_client = RCAQueryTool()

@tool
def discover_incidents() -> str:
    """Discover ServiceNow-style incidents from the same database as infrastructure."""
    try:
        # ServiceNow-style incident query using ServiceNowIncident label
        query = """
        MATCH (i:ServiceNowIncident)
        RETURN i.number as incident_number,
               i.state as state,
               i.priority as priority,
               i.severity as severity,
               i.category as category,
               i.short_description as summary,
               i.opened_at as opened_at,
               i.resolved_at as resolved_at,
               i.assigned_to as assigned_to,
               i.assignment_group as assignment_group,
               i.business_service as business_service
        ORDER BY i.opened_at DESC
        LIMIT 20
        """
        
        results = _rca_client.execute_query(query)
        
        if not results or "error" in results[0]:
            return "No incidents found in the incident management system"
        
        formatted = "ServiceNow-style Incidents Available:\n"
        formatted += "=" * 50 + "\n"
        
        for incident in results:
            formatted += f"Number: {incident.get('incident_number', 'Unknown')}\n"
            formatted += f"State: {incident.get('state', 'Unknown')}\n" 
            formatted += f"Priority: {incident.get('priority', 'Unknown')}\n"
            formatted += f"Summary: {incident.get('summary', 'Unknown')}\n"
            formatted += f"Business Service: {incident.get('business_service', 'Unknown')}\n"
            formatted += f"Opened: {incident.get('opened_at', 'Unknown')}\n"
            formatted += f"Assigned To: {incident.get('assigned_to', 'Unassigned')}\n"
            formatted += "-" * 50 + "\n"
        
        return formatted
        
    except Exception as e:
        return f"Error discovering incidents: {str(e)}"

@tool
def rca_timeline_query(incident_number: str, hours_before: int = 2, hours_after: int = 1) -> str:
    """Analyze timeline around ServiceNow incident."""
    try:
        # Get incident details
        incident_query = """
        MATCH (i:ServiceNowIncident {number: $incident_number})
        RETURN i.opened_at as opened_at,
               i.severity as severity,
               i.state as state,
               i.short_description as summary
        """
        
        incident_results = _rca_client.execute_query(incident_query, {"incident_number": incident_number})
        
        if not incident_results or "error" in incident_results[0]:
            return f"Incident {incident_number} not found."
        
        incident = incident_results[0]
        
        # Query infrastructure events around incident time
        events_query = """
        MATCH (e:Event)
        WHERE e.timestamp >= datetime($start_time) - duration({hours: $hours_before})
          AND e.timestamp <= datetime($start_time) + duration({hours: $hours_after})
        OPTIONAL MATCH (s:System)-[:HAS_EVENT]->(e)
        RETURN e.timestamp as event_time,
               e.event_type as type,
               e.description as description,
               s.prop_hostname as system
        ORDER BY e.timestamp
        """
        
        events_results = _rca_client.execute_query(events_query, {
            "start_time": incident['opened_at'],
            "hours_before": hours_before,
            "hours_after": hours_after
        })
        
        formatted = f"Timeline Analysis for {incident_number}\n"
        formatted += f"Summary: {incident.get('summary', 'Unknown')}\n"
        formatted += f"Analysis Window: {hours_before}h before to {hours_after}h after\n"
        formatted += "=" * 60 + "\n"
        
        if not events_results or (len(events_results) == 1 and events_results[0].get('event_time') is None):
            formatted += "No infrastructure events found in time window\n"
        else:
            for event in events_results:
                if event.get('event_time'):
                    formatted += f"{event['event_time']} | {event.get('system', 'Unknown')} | {event.get('type', 'Unknown')} | {event.get('description', 'No description')}\n"
        
        return formatted
        
    except Exception as e:
        return f"Timeline query error: {str(e)}"

@tool
def dependency_traversal_query(affected_system: str, max_depth: int = 3) -> str:
    """Analyze system dependencies for impact assessment."""
    try:
        query = f"""
        MATCH (start:System {{prop_hostname: $system}})
        OPTIONAL MATCH path = (start)-[:DEPENDS_ON*1..{max_depth}]->(dependent)
        RETURN start.prop_hostname as root_system,
               [node in nodes(path) | node.prop_hostname] as dependency_chain,
               length(path) as depth
        ORDER BY depth
        """
        
        results = _rca_client.execute_query(query, {"system": affected_system})
        
        if not results:
            return f"System {affected_system} not found."
        
        formatted = f"Dependency Analysis for {affected_system}\n"
        formatted += f"Analysis Depth: {max_depth} levels\n"
        formatted += "=" * 40 + "\n"
        
        for result in results:
            if result.get('dependency_chain') and len(result['dependency_chain']) > 1:
                chain = " -> ".join(result['dependency_chain'])
                formatted += f"Depth {result['depth']}: {chain}\n"
        
        return formatted
        
    except Exception as e:
        return f"Dependency traversal error: {str(e)}"

@tool
def similarity_search_analysis(search_query: str, top_k: int = 5) -> str:
    """Find similar patterns using semantic search."""
    try:
        from app.tools.vector_search import VectorSearchClient
        
        client = VectorSearchClient()
        results = client.similarity_search(search_query, k=top_k)
        
        if not results:
            return f"No similar patterns found for: {search_query}"
        
        formatted = f"Similar Pattern Analysis\n"
        formatted += f"Search Query: {search_query}\n"
        formatted += "=" * 40 + "\n"
        
        for i, (node_id, metadata) in enumerate(results, 1):
            formatted += f"{i}. {node_id}: {metadata}\n"
        
        return formatted
        
    except Exception as e:
        return f"Similarity search error: {str(e)}"
