import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings
from app.tools.neo4j_client import Neo4jClient

class VectorSearchClient:
    def __init__(self, collection_name: str = "neo4j_nodes"):
        self.client = chromadb.Client(Settings(persist_directory="./chroma_db"))
        self.collection_name = collection_name
        self.collection = None
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create or get collection, only populate if empty."""
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            doc_count = self.collection.count()
            if doc_count == 0:
                print(f"Collection {self.collection_name} is empty, populating...")
                self._populate_from_neo4j()
            else:
                print(f"Found existing collection: {self.collection_name} with {doc_count} documents")
        except Exception:
            print(f"Creating new collection: {self.collection_name}")
            self.collection = self.client.create_collection(name=self.collection_name)
            self._populate_from_neo4j()
    
    def _populate_from_neo4j(self):
        """Populate vector store with Neo4j node data."""
        print("Populating vector store from Neo4j...")
        neo4j_client = Neo4jClient()
        
        # Get all nodes with their properties
        query = """
        MATCH (n) 
        RETURN elementId(n) as id, labels(n) as labels, properties(n) as props
        LIMIT 100
        """
        
        try:
            results = neo4j_client.execute_cypher(query)
            
            documents = []
            metadatas = []
            ids = []
            
            for record in results:
                node_id = record['id']
                labels = list(record['labels'])
                props = record['props']
                
                # Create searchable text from node
                text_parts = []
                text_parts.extend(labels)
                for key, value in props.items():
                    text_parts.append(f"{key}: {value}")
                
                doc_text = " ".join(str(part) for part in text_parts)
                
                # Fix metadata - convert lists to strings and handle types
                safe_metadata = {
                    "node_id": node_id,
                    "labels": ", ".join(labels),  # Convert list to string
                    "label_count": len(labels)
                }
                
                # Add safe property values
                for key, value in props.items():
                    safe_key = f"prop_{key}"
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        safe_metadata[safe_key] = value
                    else:
                        safe_metadata[safe_key] = str(value)
                
                documents.append(doc_text)
                metadatas.append(safe_metadata)
                ids.append(node_id)
            
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"Added {len(documents)} documents to vector store")
            else:
                print("No documents to add")
            
        except Exception as e:
            print(f"Error populating vector store: {e}")
        finally:
            neo4j_client.close()
    
    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[str, Dict]]:
        """Perform similarity search and return node IDs with metadata."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            matches = []
            if results['ids'] and results['ids'][0]:
                for i, node_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    matches.append((node_id, metadata))
            
            return matches
            
        except Exception as e:
            print(f"Vector search error: {e}")
            return []

def test_vector_search():
    """Test vector search functionality."""
    client = VectorSearchClient()
    
    # Test search
    results = client.similarity_search("server", k=3)
    print(f"Search results for 'server': {results}")
    
    # Test another search
    results2 = client.similarity_search("service", k=3)
    print(f"Search results for 'service': {results2}")
    
    return len(results) > 0

if __name__ == "__main__":
    test_vector_search()
