# 🤖 xAIOps: Enterprise AI Operations Platform

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-red.svg)](https://neo4j.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An advanced multi-agent AI operations platform that revolutionizes infrastructure management through intelligent conversation-aware routing, specialized domain expertise, and sophisticated GraphRAG capabilities. Built on LangGraph with Neo4j knowledge graphs, high-performance semantic vector search, and robust multi-turn conversation handling.

## 🌟 What is xAIOps?

xAIOps is an enterprise-grade AI operations platform that combines:
- **7 Specialized Domain Agents** with pure LangGraph agentic decision-making
- **Conversation-Aware Intelligent Routing** with multi-turn context handling and autonomous reasoning
- **High-Performance GraphRAG** with 14+ Neo4j query patterns and optimized semantic search (164.9x speedup)
- **Human-in-the-Loop Workflows** with proper LangGraph interrupt() for critical security decisions
- **Agent-to-Agent Communication** for external system integration
- **Production-Ready Architecture** with robust error handling, conversation continuity, and monitoring

### 🎯 Key Use Cases

- **Infrastructure Analysis**: Comprehensive system inventory, dependency mapping, and relationship analysis
- **Security Assessment**: Vulnerability analysis, attack surface mapping, and risk prioritization with approval workflows
- **Performance Optimization**: Resource monitoring, capacity planning, and bottleneck identification
- **Incident Response**: Root cause analysis, timeline correlation, and impact assessment
- **Compliance Auditing**: Regulatory adherence tracking, policy gap analysis, and audit trail generation
- **Knowledge Management**: Pattern extraction, best practice identification, and organizational learning

## 🏗️ System Architecture

The system follows a sophisticated multi-agent architecture with intelligent routing and domain specialization:

### 🔄 Main System Flow

```mermaid
graph TD
    A[__start__] --> B[supervisor]
    
    B -->|LLM Routing Decision| C[data_domain]
    B -->|LLM Routing Decision| D[security_domain]
    B -->|LLM Routing Decision| E[performance_domain]
    B -->|LLM Routing Decision| F[compliance_domain]
    B -->|LLM Routing Decision| G[learning_domain]
    B -->|LLM Routing Decision| H[rca_domain]
    B -->|LLM Routing Decision| I[a2a_orchestrator_domain]
    
    C --> J[__end__]
    D --> J
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style J fill:#e8f5e8
    style C fill:#fff3e0
    style D fill:#ffebee
    style E fill:#f1f8e9
    style F fill:#fce4ec
    style G fill:#e0f2f1
    style H fill:#fff8e1
    style I fill:#e8eaf6
```

### 🎛️ Supervisor Routing Logic Detail

```mermaid
graph TD
    A[User Query] --> B[supervisor_node]
    B --> C[extract_user_query - Multi-turn Support]
    C --> D[build_conversation_context]
    D --> E{Try LLM Structured Routing}
    
    E -->|Success| F[RouteDecision with reasoning]
    E -->|Exception| G[Context-Aware Fallback]
    
    F --> H{Route to Domain}
    G --> I{Check Conversation Context}
    
    I -->|Security + Approval| J[security_domain]
    I -->|RCA + Approval| K[rca_domain]
    I -->|No Context Match| L[Enhanced Keyword Analysis]
    
    L -->|vulnerability, threat, cve, ssh, disable, patch| J
    L -->|incident, troubleshoot, rca| K
    L -->|performance, monitor, capacity| M[performance_domain]
    L -->|compliance, audit, policy| N[compliance_domain]
    L -->|learn, pattern, knowledge| O[learning_domain]
    L -->|external, latest, search| P[a2a_orchestrator_domain]
    L -->|Default| Q[data_domain - Pure Agentic]
    
    H --> R[Execute Domain Workflow with Agent Reasoning]
    J --> R
    K --> R
    M --> R
    N --> R
    O --> R
    P --> R
    Q --> R
    
    style E fill:#f3e5f5
    style F fill:#e8f5e8
    style G fill:#fff3e0
    style I fill:#ffebee
    style L fill:#fce4ec
    style C fill:#e1f5fe
    style Q fill:#e8f5e8
```

### 📊 Domain Agent Architecture

```mermaid
graph TD
    subgraph "Data Domain"
        DA1[graph_collector] --> DA2[context_enhancer]
        DA2 --> DA3[synthesis_node]
    end
    
    subgraph "Security Domain"
        SA1[security_analysis] --> SA2{HITL Check}
        SA2 -->|Approval Required| SA3[Interrupt for Human Input]
        SA2 -->|Approved| SA4[Continue Analysis]
    end
    
    subgraph "RCA Domain"
        RA1[discover_incidents] --> RA2[timeline_analysis]
        RA2 --> RA3[dependency_traversal]
        RA3 --> RA4[similarity_search]
    end
    
    subgraph "A2A Orchestrator"
        AA1[extract_query] --> AA2[send_to_external_agents]
        AA2 --> AA3[wait_for_completion]
        AA3 --> AA4[return_response]
    end
    
    style SA3 fill:#ffcdd2
    style AA2 fill:#e8eaf6
```

### 🧠 Intelligent Supervisor System

**Multi-Tier Routing Strategy:**
1. **Primary Route**: LLM-powered routing with Pydantic structured outputs and reasoning transparency
2. **Context-Aware Fallback**: Conversation history analysis with domain continuity 
3. **Enhanced Keyword Fallback**: Expanded security action recognition (ssh, disable, patch, cve) with guaranteed routing
4. **Pure Agentic Execution**: Within domains, agents autonomously decide query parameters and strategies

**Advanced Features:**
- **Multi-turn Conversation Handling**: Fixed message extraction (state["messages"][-1]) for seamless follow-ups
- **Domain Continuity**: Routes follow-up questions to appropriate ongoing conversations
- **Enhanced Security Routing**: Expanded action-oriented keyword recognition (ssh, disable, patch, cve)
- **Pure Agentic Domain Execution**: Within domains, agents autonomously decide query parameters and strategies
- **Approval Flow Handling**: LangGraph interrupt() for proper Human-in-the-Loop workflows
- **Error Resilience**: Graceful degradation through multiple fallback layers

### 🎯 Domain-Specialized Agents (7 Expert Systems)

| Domain | Purpose | Key Capabilities | Tools Used |
|--------|---------|------------------|------------|
| **Data Domain** | Infrastructure inventory & analysis | Pure agentic query strategy, intelligent parameter selection, multi-turn conversation handling | Neo4j (14 query types), Vector search |
| **Security Domain** | Cybersecurity analysis & risk assessment | Vulnerability analysis, attack surface mapping, HITL approval | Enhanced GraphRAG, Security correlation |
| **Performance Domain** | Resource optimization & monitoring | Capacity planning, bottleneck identification, metrics analysis | Performance analytics, Trend analysis |
| **Compliance Domain** | Regulatory adherence & auditing | Policy gap analysis, audit trails, regulatory mapping | Compliance frameworks, Documentation |
| **Learning Domain** | Knowledge extraction & pattern analysis | Conversation analysis, best practice extraction, knowledge updates | Pattern recognition, Learning algorithms |
| **RCA Domain** | Root cause analysis & incident response | Timeline correlation, dependency impact, incident analysis | Advanced graph traversal, Temporal analysis |
| **A2A Orchestrator** | External system integration | Web search, real-time data, external agent coordination | A2A SDK, External APIs |

### 🛠️ Technology Stack

**Core Framework:**
- **[LangGraph 0.2.0+](https://langchain-ai.github.io/langgraph/)**: State-based agent orchestration with conditional routing and built-in persistence (no custom checkpointers needed)
- **[Python 3.11+](https://www.python.org/)**: Modern Python with type hints and async support

**AI & Language Models:**
- **[LangChain Core 0.3.0+](https://python.langchain.com/)**: LLM integration and tool calling
- **Custom LLM Integration**: Llama-4-Scout-17B with structured output support
- **[Pydantic 2.0+](https://pydantic.dev/)**: Type-safe structured outputs and validation

**Data & Knowledge:**
- **[Neo4j 5.0+](https://neo4j.com/)**: Knowledge graph database with advanced Cypher patterns
- **[ChromaDB 0.4.0+](https://www.trychroma.com/)**: High-performance vector embeddings with global singleton optimization (164.9x speedup)
- **Enhanced GraphRAG**: 14+ specialized query patterns with intelligent agentic parameter selection

**Communication & Integration:**
- **[A2A SDK 0.2.6+](https://github.com/meta-llama/llama-stack)**: Agent-to-agent communication protocol
- **[FastAPI 0.104.0+](https://fastapi.tiangolo.com/)**: High-performance API framework
- **[HTTPX 0.25.0+](https://www.python-httpx.org/)**: Async HTTP client for external integrations

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with pip and virtual environment support
- **Neo4j Desktop** or Neo4j server instance
- **Custom LLM Endpoint** (Llama-4-Scout-17B or compatible)
- **Git** for cloning the repository

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/xaiops-graphrag.git
cd xaiops-graphrag

# Create and activate Python 3.11 virtual environment
python3.11 -m venv .venv311
source .venv311/bin/activate  # On Windows: .venv311\Scripts\activate

# Install dependencies
pip install -e .
pip install -U "langgraph-cli[inmem]"
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

# LLM Configuration
LLM_BASE_URL=https://your-llm-endpoint.com:443/v1
LLM_API_KEY=your_api_key_here
LLM_MODEL_NAME=llama-4-scout-17b-16e-w4a16

# Optional: Vector Store Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Optional: A2A Configuration (for external agent integration)
A2A_ORCHESTRATOR_URL=http://localhost:8000
A2A_WEB_SEARCH_URL=http://localhost:8002
```

### 3. Database Setup

**Neo4j Setup:**
1. Install and start Neo4j Desktop
2. Create a new database or use existing
3. Populate with your infrastructure data

**Vector Store Setup:**
```bash
# The system will automatically populate ChromaDB from Neo4j data
# Optimized with global singleton pattern for 164.9x performance improvement
# Data loads once on first request, then reuses in-memory collection
# Ensure your infrastructure metadata is available at the configured path
```

### 4. Launch the System

```bash
# Start the LangGraph development server
langgraph dev
```

The system will be available at:
- **🌐 API Endpoints**: http://127.0.0.1:2024/docs
- **🎨 LangGraph Studio**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- **📊 Health Check**: http://127.0.0.1:2024/health

## 📖 Usage Examples

### Basic Infrastructure Queries

```bash
# Count all servers in infrastructure
curl -X POST "http://127.0.0.1:2024/runs/wait" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "xaiops",
    "input": {
      "messages": [{"role": "user", "content": "Count all servers in our infrastructure"}]
    }
  }'
```

### Security Analysis

```bash
# Comprehensive security vulnerability assessment
curl -X POST "http://127.0.0.1:2024/runs/wait" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "xaiops",
    "input": {
      "messages": [{"role": "user", "content": "Analyze security vulnerabilities requiring approval"}]
    }
  }'
```

### Performance Analysis

```bash
# Performance bottleneck identification
curl -X POST "http://127.0.0.1:2024/runs/wait" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "xaiops",
    "input": {
      "messages": [{"role": "user", "content": "Identify performance bottlenecks in payment services"}]
    }
  }'
```

### Root Cause Analysis

```bash
# Incident investigation with timeline analysis
curl -X POST "http://127.0.0.1:2024/runs/wait" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "xaiops",
    "input": {
      "messages": [{"role": "user", "content": "Analyze incident INC001234 with dependency impact"}]
    }
  }'
```

### Streaming Responses

```bash
# Real-time streaming for complex analysis
curl -X POST "http://127.0.0.1:2024/runs/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "xaiops",
    "input": {
      "messages": [{"role": "user", "content": "Comprehensive infrastructure health assessment"}]
    },
    "stream_mode": "values"
  }'
```

## 📁 Project Structure

```
xaiops-graphrag/
├── 📄 README.md                     # This comprehensive guide
├── 📄 LICENSE                       # MIT License
├── 📄 pyproject.toml                # Python project configuration
├── 📄 langgraph.json               # LangGraph server configuration
├── 📄 .env                         # Environment variables (create this)
│
├── 📂 src/app/                      # Main application source
│   ├── 📄 main.py                  # LangGraph server entry point
│   ├── 📄 llm_config.py            # LLM configuration and initialization
│   ├── 📄 state.py                 # State management for LangGraph workflows
│   │
│   ├── 📂 graphs/                   # LangGraph workflow definitions
│   │   ├── 📄 supervisor.py        # Intelligent routing supervisor
│   │   ├── 📄 domain_subgraphs.py  # Domain-specific agent workflows
│   │   ├── 📄 rca_subgraph.py      # Root cause analysis workflows
│   │   └── 📄 a2a_orchestrator_subgraph.py  # External agent integration
│   │
│   ├── 📂 tools/                    # AI agent tools and integrations
│   │   ├── 📄 data_tools.py        # Enhanced Neo4j tools (14 query types)
│   │   ├── 📄 vector_search.py     # ChromaDB semantic search
│   │   ├── 📄 rca_tools.py         # Root cause analysis tools
│   │   └── 📄 hitl_tools.py        # Human-in-the-loop workflow tools
│   │
│   ├── 📂 prompts/                  # Agent behavior definitions
│   │   ├── 📄 security_domain.md   # Security analysis framework
│   │   ├── 📄 performance_domain.md # Performance optimization framework
│   │   ├── 📄 compliance_domain.md # Compliance auditing framework
│   │   ├── 📄 rca_domain.md        # Root cause analysis framework
│   │   ├── 📄 learning_domain.md   # Knowledge extraction framework
│   │   ├── 📄 graph_collector.md   # Graph query strategy framework
│   │   └── 📄 vector_collector.md  # Semantic search framework
│   │
│   ├── 📄 a2a_orchestrator.py      # A2A agent coordination
│   ├── 📄 a2a_agent_executor.py    # A2A execution framework
│   ├── 📄 a2a_ops_server.py        # A2A operations server
│   └── 📄 llamastack_a2a_agent.py  # LlamaStack integration
│
└── 📂 chroma_db/                   # ChromaDB vector store (auto-created)
```

## 🔧 Advanced Configuration

### Intelligent Query Strategy 

The system uses **Pure LangGraph Agentic Approach** for intelligent query parameter selection:

**Autonomous Decision-Making:**
- **Intent Recognition**: Agents understand user intent (count, inventory, analysis, etc.)
- **Parameter Selection**: Intelligent mapping of natural language to optimal query parameters  
- **Environment Handling**: Automatic filtering for production, staging, dev environments
- **Synonym Recognition**: Handles "nodes", "servers", "machines", "hosts" seamlessly

**Available Query Types (Agent-Selected):**
- `systems`: Infrastructure inventory and server discovery
- `services`: Application services and health status  
- `vulnerabilities`: Security vulnerability assessment
- `events`: Operational events and incident tracking
- `dependencies`: Service dependency mapping
- `overview`: High-level infrastructure overview
- `system_neighbors`: Direct relationship neighborhood analysis
- `vulnerability_impact`: Enhanced impact assessment with affected entities
- `service_health`: Service status with dependency context
- `incident_correlation`: System-incident relationship mapping
- `dependency_path`: Shortest path analysis between systems
- `system_context`: Rich contextual information with multi-hop relationships
- `search`: Keyword-based entity discovery across all properties
- `cypher`: Custom Cypher query execution for complex patterns

**Performance Optimizations:**
- **Vector Search**: Global singleton pattern with 164.9x performance improvement
- **Multi-turn Conversations**: Proper message extraction for seamless follow-ups
- **Conversation Context**: Maintains query history and domain continuity

### Agent Prompt Customization

Each domain agent uses sophisticated prompt frameworks located in `src/app/prompts/`. These can be customized for your specific infrastructure and organizational needs:

```bash
# Example: Customize security analysis framework
vim src/app/prompts/security_domain.md

# Example: Modify RCA methodology
vim src/app/prompts/rca_domain.md
```

### Human-in-the-Loop Configuration

Security and compliance workflows include HITL gates for critical decisions using LangGraph's interrupt() function:

```python
# Example: Configure security approval thresholds
# In src/app/tools/hitl_tools.py
from langgraph.types import interrupt

@tool
def security_approval_gate(finding: str, risk_level: str) -> str:
    """Proper LangGraph HITL implementation with interrupt()"""
    # Use LangGraph interrupt to pause execution and wait for human input
    response = interrupt({
        "type": "security_approval",
        "finding": finding,
        "risk_level": risk_level,
        "question": f"⚠️ SECURITY APPROVAL REQUIRED\n\nAction: {finding}\nRisk Level: {risk_level}\n\nDo you approve this action?",
        "options": ["approve", "deny"]
    })
    
    if response and response.lower() in ["approve", "approved", "yes", "y"]:
        return f"✅ APPROVED: {finding} - Proceeding with security action"
    else:
        return f"❌ DENIED: {finding} - Security action blocked by human reviewer"
```

## 🧪 Development Guide

### Local Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Type checking
mypy src/

# Code formatting
black src/
ruff check src/
```

### Creating Custom Domain Agents

1. **Create Domain Subgraph:**
```python
# src/app/graphs/my_domain_subgraph.py
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import create_react_agent

def create_my_domain_subgraph():
    workflow = StateGraph(MessagesState)
    
    my_agent = create_react_agent(
        model=get_llm(),
        tools=[your_custom_tools],
        prompt=load_prompt("my_domain"),
        name="my_agent"
    )
    
    workflow.add_node("my_agent", my_agent)
    workflow.add_edge(START, "my_agent")
    workflow.add_edge("my_agent", END)
    
    return workflow.compile()
```

2. **Create Domain Prompt:**
```markdown
<!-- src/app/prompts/my_domain.md -->
You are an expert in [your domain] performing [specific analysis type].

## Analysis Framework
1. **Discovery Phase**: Use [specific tools] to gather initial data
2. **Assessment Phase**: Analyze findings using [methodology]
3. **Reporting Phase**: Provide structured recommendations

## Tool Usage Guidelines
- Use [tool_name] for [specific purpose]
- Apply [methodology] for [analysis type]

## Output Format
**[SECTION NAME]**
- Key Finding: [Details]
- Confidence Level: [High/Medium/Low]
- Recommendations: [Action items]
```

3. **Register in Supervisor:**
```python
# Add to src/app/graphs/supervisor.py
from app.graphs.my_domain_subgraph import create_my_domain_subgraph

# In create_supervisor() function:
workflow.add_node("my_domain", create_my_domain_subgraph())
```

### Custom Tool Development

```python
# src/app/tools/my_tools.py
from langchain_core.tools import tool

@tool
def my_analysis_tool(query: str, depth: int = 5) -> str:
    """
    Custom analysis tool for your specific domain.
    
    Args:
        query: Analysis query or target system
        depth: Analysis depth (1-10)
    
    Returns:
        Formatted analysis results
    """
    try:
        # Your custom analysis logic
        results = perform_analysis(query, depth)
        return format_results(results)
    except Exception as e:
        return f"Analysis error: {str(e)}"
```

## ⚠️ Troubleshooting

### Common Issues

**Connection Problems:**
```bash
# Check Neo4j connectivity
neo4j status

# Verify environment variables
echo $NEO4J_URI
echo $LLM_BASE_URL

# Test LLM endpoint
curl -H "Authorization: Bearer $LLM_API_KEY" $LLM_BASE_URL/v1/models
```

**Performance Issues:**
```bash
# Monitor LangGraph execution
tail -f langgraph.log

# Check Neo4j query performance
# In Neo4j Browser: :queries

# Vector store status
ls -la chroma_db/
```

**Memory Issues:**
```bash
# Reduce concurrent requests
export LANGGRAPH_MAX_WORKERS=2

# Increase timeout for complex queries
export LANGGRAPH_TIMEOUT=300
```

### Debug Mode

```bash
# Enable detailed logging
export LANGGRAPH_DEBUG=true
export PYTHONPATH=$PWD/src

# Run with debug output
langgraph dev --debug
```

### Data Schema Validation

Ensure your Neo4j database contains the expected node types and relationships:

```cypher
// Required node types
MATCH (n) RETURN DISTINCT labels(n) AS node_types;

// Required relationships  
MATCH ()-[r]->() RETURN DISTINCT type(r) AS relationship_types;

// Sample data check
MATCH (s:System) RETURN count(s) AS system_count;
MATCH (svc:Service) RETURN count(svc) AS service_count;
```

## 🔍 API Reference

### Core Endpoints

**Execute Analysis (Synchronous):**
```http
POST /runs/wait
Content-Type: application/json

{
  "assistant_id": "xaiops",
  "input": {
    "messages": [{"role": "user", "content": "Your query here"}]
  }
}
```

**Execute Analysis (Streaming):**
```http
POST /runs/stream
Content-Type: application/json

{
  "assistant_id": "xaiops", 
  "input": {
    "messages": [{"role": "user", "content": "Your query here"}]
  },
  "stream_mode": "values"
}
```

**Health Check:**
```http
GET /health
```

**System Status:**
```http
GET /assistants
```

### Query Categories

**Infrastructure Analysis:**
- "Count all servers"
- "Show database systems"
- "Map service dependencies"
- "Find system neighbors for [system_name]"

**Security Assessment:**
- "Analyze security vulnerabilities"
- "Map attack surface for [system]"
- "Check vulnerability impact for [CVE-ID]"
- "Security review for [finding]"

**Performance Analysis:**
- "Identify performance bottlenecks"
- "Analyze resource utilization" 
- "Check service health for [service]"
- "Performance trends for [system]"

**Incident Response:**
- "Analyze incident [incident_id]"
- "Root cause analysis for [issue]"
- "Timeline analysis for [timeframe]"
- "Impact assessment for [system]"

## 🤝 Contributing

We welcome contributions! Please see our contribution guidelines:

### Development Workflow

1. **Fork the repository** and create a feature branch
2. **Set up development environment** following the guide above
3. **Make your changes** with appropriate tests
4. **Run the test suite** to ensure no regressions
5. **Submit a pull request** with detailed description

### Contribution Areas

- **Domain Agents**: New specialized analysis domains
- **Tools & Integrations**: Additional data sources and APIs
- **Query Patterns**: Enhanced Neo4j and vector search capabilities
- **Documentation**: Tutorials, examples, and guides
- **Testing**: Test coverage and integration tests
- **Performance**: Optimization and scalability improvements

### Code Standards

- **Python 3.11+** with type hints
- **Black** for code formatting
- **Ruff** for linting
- **Pytest** for testing
- **Comprehensive docstrings** for all functions
- **Type safety** with Pydantic models

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph Team** for the agent orchestration framework
- **Neo4j** for the graph database technology
- **LangChain** for LLM integration capabilities
- **ChromaDB** for vector search functionality
- **A2A Protocol** for agent-to-agent communication standards

## 📞 Support

- **Documentation**: [Project Wiki](https://github.com/your-org/xaiops-graphrag/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/xaiops-graphrag/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/xaiops-graphrag/discussions)
- **Security**: Email security@your-org.com for security-related issues

---

**Built with ❤️ for the AI Operations Community**

