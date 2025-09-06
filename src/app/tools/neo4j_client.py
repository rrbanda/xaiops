import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from neo4j import GraphDatabase
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = None
    
    def connect(self):
        """Establish connection to Neo4j."""
        if not self.driver:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
    
    def close(self):
        """Close connection."""
        if self.driver:
            self.driver.close()
    
    def execute_cypher(self, query: str, parameters: Dict = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        self.connect()
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                records = []
                for record in result:
                    records.append(dict(record))
                return records
        except Exception as e:
            print(f"Cypher execution error: {e}")
            return []
    
    def get_schema(self) -> Dict[str, Any]:
        """Get basic database schema information."""
        schema_queries = {
            "node_labels": "CALL db.labels()",
            "relationship_types": "CALL db.relationshipTypes()",
            "node_counts": """
                MATCH (n) 
                RETURN labels(n)[0] as label, count(n) as count 
                ORDER BY count DESC
            """
        }
        
        schema = {}
        for key, query in schema_queries.items():
            try:
                schema[key] = self.execute_cypher(query)
            except Exception as e:
                schema[key] = f"Error: {e}"
        
        return schema

def test_neo4j_client():
    """Test the Neo4j client."""
    client = Neo4jClient()
    
    # Test basic query
    result = client.execute_cypher("RETURN 'Hello Neo4j' as greeting")
    print(f"Basic query result: {result}")
    
    # Test schema
    schema = client.get_schema()
    print(f"Schema: {schema}")
    
    client.close()
    return True

if __name__ == "__main__":
    test_neo4j_client()
