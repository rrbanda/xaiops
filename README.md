# xAIOps Agentic GraphRAG

An intelligent retrieval-augmented generation system that combines Neo4j graph database queries with semantic vector search using specialized AI agents. The system intelligently routes questions to appropriate retrieval methods and provides contextual responses about infrastructure data.

## Architecture

**Agentic Multi-Agent System:**
- **Graph Agent**: Handles structured database queries, counts, and precise entity lookups using Cypher
- **Vector Agent**: Performs semantic similarity searches for related/similar content discovery
- **Intelligent Router**: Keyword-based routing that dispatches queries to appropriate specialist agents

**Technology Stack:**
- **LangGraph**: Agent orchestration and workflow management
- **Neo4j**: Graph database for infrastructure relationships
- **ChromaDB**: Vector storage for semantic search
- **Custom LLM**: Llama-4-Scout-17B endpoint for natural language processing

## Prerequisites

- Python 3.11+
- Neo4j Desktop (running locally)
- Custom LLM API access

## Installation

### 1. Environment Setup

```bash
# Create Python 3.11 virtual environment
python3.11 -m venv .venv311
source .venv311/bin/activate

# Install dependencies
pip install -e .
pip install -U "langgraph-cli[inmem]"
```

### 2. Configuration

Create `.env` file with your credentials:

```bash
# Neo4j Configuration (local desktop default)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=neo4j

# Custom LLM Configuration
LLM_BASE_URL=https://your-llm-endpoint.com:443/v1
LLM_API_KEY=your_api_key_here
LLM_MODEL_NAME=llama-4-scout-17b-16e-w4a16
```

### 3. Data Prerequisites

Ensure your Neo4j database contains nodes with:
- Server nodes with properties
- Service nodes with relationships
- Any infrastructure data for testing

## Running the System

### Start LangGraph Server

```bash
langgraph dev
```

The server will start on `http://127.0.0.1:2024` with:
- **API Endpoints**: http://127.0.0.1:2024/docs
- **LangGraph Studio**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

## Usage

### Basic Query Examples

**Count Infrastructure Nodes:**
```bash
curl -s --request POST \
    --url "http://127.0.0.1:2024/runs/wait" \
    --header 'Content-Type: application/json' \
    --data '{
        "assistant_id": "graphrag_supervisor",
        "input": {
            "messages": [{"role": "user", "content": "Count all servers"}]
        }
    }'
```

**Find Similar Infrastructure:**
```bash
curl -s --request POST \
    --url "http://127.0.0.1:2024/runs/wait" \
    --header 'Content-Type: application/json' \
    --data '{
        "assistant_id": "graphrag_supervisor",
        "input": {
            "messages": [{"role": "user", "content": "Find servers similar to web production"}]
        }
    }'
```

**Streaming Response:**
```bash
curl -s --request POST \
    --url "http://127.0.0.1:2024/runs/stream" \
    --header 'Content-Type: application/json' \
    --data '{
        "assistant_id": "graphrag_supervisor",
        "input": {
            "messages": [{"role": "user", "content": "Show me database servers"}]
        },
        "stream_mode": "values"
    }'
```

## Project Structure

```
src/app/
├── main.py                    # LangGraph server entry point
├── llm_config.py             # LLM configuration
├── agents/
│   ├── specialists.py        # Graph and vector specialist agents
│   └── supervisor.py         # Main routing supervisor
└── tools/
    ├── agent_tools.py        # Neo4j and vector search tools
    ├── neo4j_client.py       # Database client
    └── vector_search.py      # Vector search with ChromaDB

langgraph.json                # LangGraph server configuration
```

## How It Works

### Query Flow

1. **Question Analysis**: Router analyzes incoming questions for keywords
2. **Agent Selection**: 
   - Graph Agent: "count", "show", "list", "how many"
   - Vector Agent: "similar", "related", "like", "find"
3. **Tool Execution**: Selected agent autonomously calls appropriate tools
4. **Response Generation**: Agent synthesizes results into natural language

### Agent Capabilities

**Graph Agent:**
- Generates clean Cypher queries
- Executes structured database operations
- Handles counts, specific entity lookups, relationship traversals

**Vector Agent:**
- Performs semantic similarity search
- Finds conceptually related infrastructure components
- Provides context-aware recommendations

## Key Features

- **Autonomous Tool Selection**: Agents independently choose and execute tools
- **Intelligent Routing**: Keyword-based dispatch to appropriate specialists
- **Self-Termination**: Agents complete tasks and stop appropriately
- **Error Resilience**: Robust handling of query failures and edge cases
- **Production-Ready**: Official LangGraph server with professional API endpoints

## Development

### Local Testing

```bash
# Test individual components
python src/app/agents/specialists.py

# Test full supervisor
python src/app/main.py
```

### Debugging

Access LangGraph Studio for visual debugging:
- Navigate to: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- Visualize agent interactions and tool calls
- Debug routing decisions and execution flows

## Troubleshooting

**Connection Issues:**
- Verify Neo4j Desktop is running
- Check LLM endpoint accessibility
- Confirm environment variables are set

**Query Failures:**
- Review Cypher query generation in logs
- Check vector store population status
- Verify agent routing decisions

**Performance:**
- Monitor token usage in responses
- Check vector search relevance
- Optimize Cypher query patterns

## Contributing

This system demonstrates agentic behavior through:
- Autonomous decision-making within agents
- Dynamic tool usage based on context
- Self-contained task completion
- Intelligent routing and orchestration

The architecture balances deterministic routing (reliability) with agentic execution (flexibility), providing a robust foundation for intelligent infrastructure queries.
