from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings
import json
from pathlib import Path

class VectorSearchClient:
    def __init__(self, collection_name: str = "infrastructure_embeddings", lazy_init: bool = False):
        self.client = chromadb.Client(Settings(persist_directory="./chroma_db"))
        self.collection_name = collection_name
        self.collection = None
        self._initialized = False
        self.lazy_init = lazy_init
        
        if not lazy_init:
            self._ensure_collection()
    
    def ensure_initialized(self):
        """Ensure vector store is initialized - only loads data once."""
        if self._initialized:
            return
            
        try:
            # Try to get existing collection first
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                print(f"Found existing collection: {self.collection_name}")
                # Check if collection has data
                count = self.collection.count()
                if count > 0:
                    print(f"Using existing collection with {count} documents")
                    self._initialized = True
                    return
                else:
                    print("Collection exists but is empty, repopulating...")
            except:
                print(f"Collection {self.collection_name} not found, creating new one...")
            
            # Create or recreate collection
            try:
                self.client.delete_collection(name=self.collection_name)
            except:
                pass
            
            print(f"Creating new collection: {self.collection_name}")
            self.collection = self.client.create_collection(name=self.collection_name)
            self._populate_from_generated_data()
            self._initialized = True
            
        except Exception as e:
            print(f"Error initializing collection: {e}")
            # Create empty collection as fallback
            try:
                self.collection = self.client.create_collection(name=self.collection_name)
                self._initialized = True
            except:
                pass
    
    def _ensure_collection(self):
        """Legacy method for backwards compatibility."""
        self.ensure_initialized()
    
    def _populate_from_generated_data(self):
        """Populate with actual generated infrastructure data."""
        print("Populating vector store with generated infrastructure data...")
        
        # Load from your generated metadata
        metadata_path = Path("/Users/raghurambanda/dataloader/simulated_rhel_systems/_agent_metadata/nodes.json")
        
        if not metadata_path.exists():
            print("Generated metadata not found, using sample data")
            self._populate_sample_data()
            return
        
        with open(metadata_path, 'r') as f:
            nodes_data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        for node in nodes_data:
            if 'Server' in node.get('labels', []):
                # Create searchable text from server properties
                props = node.get('properties', {})
                text_parts = []
                
                # Add server type and environment info
                hostname = props.get('prop_hostname', node['id'])
                environment = props.get('environment', 'unknown')
                business_service = props.get('prop_business_service', 'system')
                team_owner = props.get('prop_team_owner', 'unknown')
                
                text_parts.append(f"{hostname} {environment} server")
                text_parts.append(f"{business_service.replace('_', ' ')}")
                text_parts.append(f"managed by {team_owner.replace('_', ' ')}")
                
                # Add technical details
                if 'web' in node['id']:
                    text_parts.append("web server apache nginx http https production")
                elif 'db' in node['id']:
                    text_parts.append("database server mysql postgresql data storage")
                elif 'api' in node['id']:
                    text_parts.append("api server rest microservices integration")
                elif 'cache' in node['id']:
                    text_parts.append("cache server redis memcached performance")
                elif 'analytics' in node['id']:
                    text_parts.append("analytics server data processing elasticsearch")
                elif 'monitor' in node['id']:
                    text_parts.append("monitoring server metrics prometheus grafana")
                elif 'app' in node['id']:
                    text_parts.append("application server java tomcat business logic")
                elif 'file' in node['id']:
                    text_parts.append("file server storage nfs backup")
                
                doc_text = " ".join(text_parts)
                
                # Create clean metadata
                metadata = {
                    "labels": "Server",
                    "prop_hostname": hostname,
                    "prop_environment": environment,
                    "prop_business_service": business_service,
                    "prop_team_owner": team_owner,
                    "prop_ip": props.get('prop_ip', '10.1.1.100'),
                    "prop_criticality": props.get('criticality', 'medium')
                }
                
                documents.append(doc_text)
                metadatas.append(metadata)
                ids.append(node['id'])
        
        if documents:
            # Add in batches to avoid memory issues
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_meta = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_meta,
                    ids=batch_ids
                )
            
            print(f"Added {len(documents)} generated infrastructure systems to vector store")
        else:
            print("No server data found, using sample data")
            self._populate_sample_data()
    
    def _populate_sample_data(self):
        """Fallback sample data if generated data not available."""
        sample_data = [
            {
                "id": "web-prod-sample",
                "text": "web server production environment apache nginx",
                "metadata": {"labels": "Server", "prop_environment": "production"}
            }
        ]
        
        documents = [item["text"] for item in sample_data]
        metadatas = [item["metadata"] for item in sample_data]
        ids = [item["id"] for item in sample_data]
        
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
    
    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[str, Dict]]:
        """Perform similarity search and return node IDs with metadata."""
        try:
            # Ensure we're initialized before searching
            self.ensure_initialized()
            
            if not self.collection:
                print("Vector collection not available")
                return []
            
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

if __name__ == "__main__":
    # Test the lazy initialization
    client = VectorSearchClient(lazy_init=True)
    print("Vector client created with lazy initialization")
    
    # Force initialization
    client.ensure_initialized()
    print("Vector store initialized with generated data!")
