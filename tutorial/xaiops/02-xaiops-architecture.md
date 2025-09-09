# XAI Ops Architecture: LangGraph in Action

Now that you understand LangGraph concepts, let's see how XAI Ops implements them to create an enterprise AI orchestration system.

## 🏗️ The Big Picture: Multi-Agent Enterprise System

```
                    🌐 USER QUERIES
                          │
                    ┌─────▼─────┐
                    │ SUPERVISOR │ ◄─── Smart Router (Main Graph)
                    │   (Graph)  │
                    └─────┬─────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼───┐       ┌─────▼─────┐    ┌─────▼─────┐
   │ DATA   │       │ SECURITY  │    │    RCA    │
   │DOMAIN  │       │  DOMAIN   │    │  DOMAIN   │ ◄─── Specialized Departments (Subgraphs)
   │        │       │           │    │           │
   │🗄️+🔍+🎯│       │🔒+👤+✅   │    │📊+🔍+⏱️ │ ◄─── Expert Workers (Agents)
   └────────┘       └───────────┘    └───────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                    ┌─────▼─────┐
                    │  RESPONSE │ ◄─── Final Product
                    └───────────┘
```

## 📁 Codebase Structure Mapping

```
src/app/
├── graph.py                    # 🏭 Main factory entry point
├── main.py                     # 🚀 Application launcher
├── graphs/
│   ├── supervisor.py           # 🎼 Orchestra conductor (Main Graph)
│   ├── domain_subgraphs.py     # 🏢 Department workflows (Subgraphs)
│   ├── rca_subgraph.py         # 📊 Incident analysis department
│   └── a2a_orchestrator_subgraph.py # 🌐 External coordination
├── tools/                      # 🔧 Worker toolkits
├── prompts/                    # 📚 Worker training manuals
└── state.py                    # 📋 Shared clipboard format
```

## 🎼 The Supervisor: Your Orchestra Conductor

**File**: `src/app/graphs/supervisor.py`

### 🧠 How It Works
```python
def create_supervisor():
    """The main conductor that routes queries to expert departments"""
    workflow = StateGraph(MessagesState)  # Create the orchestra
    
    # Add all the specialized departments (subgraphs)
    workflow.add_node("data_domain", create_data_subgraph())
    workflow.add_node("security_domain", create_security_subgraph())
    workflow.add_node("rca_domain", create_rca_subgraph())
    workflow.add_node("performance_domain", create_performance_subgraph())
    workflow.add_node("compliance_domain", create_compliance_subgraph())
    workflow.add_node("learning_domain", create_learning_subgraph())
    workflow.add_node("a2a_orchestrator_domain", create_a2a_orchestrator_subgraph())
```

### 🚦 Smart Routing Logic
```python
def route_query(state):
    """The conductor's decision: which section should play this piece?"""
    user_query = extract_user_query(state).lower()
    
    # Pattern matching like a smart receptionist
    if any(word in user_query for word in ["security", "vulnerability", "breach"]):
        return "security_domain"    # Send to security experts
    elif any(word in user_query for word in ["incident", "outage", "root cause"]):
        return "rca_domain"         # Send to incident analysts
    elif any(word in user_query for word in ["performance", "slow", "latency"]):
        return "performance_domain" # Send to performance experts
    elif any(word in user_query for word in ["web", "search", "news", "current"]):
        return "a2a_orchestrator_domain"  # Send to external search
    else:
        return "data_domain"        # Default: infrastructure data
```

**Real-World Analogy**: Like a hospital triage nurse who reads your symptoms and immediately knows whether to send you to emergency, cardiology, or general practice.

## 🏢 Department Deep-Dive: Data Domain Subgraph

**File**: `src/app/graphs/domain_subgraphs.py`

### 🏭 The Hybrid RAG Assembly Line

Your data domain implements a sophisticated **sequential dual-source RAG** pattern:

```python
def create_data_subgraph():
    """A specialized data analysis department with its own workflow"""
    
    # 🧠 Expert Workers (Created once, reused forever)
    graph_agent = create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool],           # Database toolkit
        prompt="You are a database expert...", # Training manual
        name="graph_collector"
    )
    
    vector_agent = create_react_agent(
        model=get_llm(), 
        tools=[vector_search_tool],         # Search toolkit
        prompt="You are a semantic search expert...", # Training manual
        name="context_enhancer"
    )
    
    # 🏭 Assembly Line Setup
    workflow = StateGraph(MessagesState)
    workflow.add_node("graph_collector", graph_agent)    # Station 1: Get structured data
    workflow.add_node("context_enhancer", vector_agent)  # Station 2: Get contextual patterns
    workflow.add_node("synthesis", synthesis_node)       # Station 3: Combine intelligently
    
    # 🚚 Conveyor Belt Flow
    workflow.add_edge(START, "graph_collector")          # Always start with structured data
    workflow.add_edge("graph_collector", "context_enhancer")  # Then add context
    workflow.add_edge("context_enhancer", "synthesis")   # Finally synthesize
    workflow.add_edge("synthesis", END)                  # Package and ship
```

### 🔄 The Assembly Line in Action

**Step 1**: Graph Collector (Database Expert)
```
Input: "How many production servers do we have?"
Agent thinks: "This needs a 'systems' query with search_term='production'"
Tool call: neo4j_query_tool(query_type="systems", search_term="production")
Output: "Found 45 production servers: web-prod-01, db-prod-02..."
```

**Step 2**: Context Enhancer (Pattern Expert) 
```
Input: Same user query + previous results
Agent thinks: "Let me find similar server configurations and patterns"
Tool call: vector_search_tool(query="production server configuration environment")
Output: "Similar patterns: high-availability setups, load balancer configs..."
```

**Step 3**: Synthesis (Assembly Worker)
```
Input: Structured data + contextual patterns
Process: Combine using intelligent synthesis prompt
Output: "You have 45 production servers. Based on patterns, these follow
         standard HA configuration with load balancers. Recommendations: ..."
```

## 🔒 Specialized Department: Security Domain

**File**: `src/app/graphs/domain_subgraphs.py`

```python
def create_security_subgraph():
    """Security department with human oversight"""
    workflow = StateGraph(MessagesState)
    
    # 🛡️ Security Expert with Special Tools
    security_agent = create_react_agent(
        model=get_llm(),
        tools=[
            neo4j_query_tool,        # Database access
            vector_search_tool,      # Pattern analysis  
            security_approval_gate   # 👤 Human-in-the-loop control
        ],
        prompt=load_prompt("security_domain"),  # Security-specific training
        name="security_agent"
    )
    
    workflow.add_node("security_agent", security_agent)
    workflow.add_edge(START, "security_agent")
    workflow.add_edge("security_agent", END)
    
    return workflow.compile()
```

**Key Feature**: The `security_approval_gate` tool implements **Human-in-the-Loop (HITL)** pattern for sensitive security operations.

## 📊 Specialized Department: RCA Domain

**File**: `src/app/graphs/rca_subgraph.py`

```python
def create_rca_subgraph():
    """Incident analysis department with specialized tools"""
    rca_agent = create_react_agent(
        model=get_llm(),
        tools=[
            discover_incidents,              # 🔍 Find related incidents
            rca_timeline_query,             # ⏰ Build incident timeline  
            dependency_traversal_query,     # 🕸️ Map system dependencies
            similarity_search_analysis,     # 🔍 Find similar past incidents
            neo4j_query_tool,              # 📊 General database access
            vector_search_tool             # 🧠 Pattern matching
        ],
        prompt=load_prompt("rca_domain"),   # RCA methodology training
        name="rca_agent"
    )
```

**Intelligence**: This agent can autonomously decide which RCA tools to use and in what order based on the incident description.

## 🌐 External Integration: A2A Orchestrator

**File**: `src/app/graphs/a2a_orchestrator_subgraph.py`

```python
def create_a2a_orchestrator_subgraph():
    """External AI coordination department"""
    
    async def a2a_orchestrator_node(state):
        """Coordinate with external AI agents"""
        # Create A2A JSON-RPC request
        payload = {
            "jsonrpc": "2.0",
            "method": "message/send", 
            "params": {"message": {"role": "user", "parts": [{"text": query}]}}
        }
        
        # Call external AI orchestrator and wait for response
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000", json=payload)
            return parse_external_response(response)
```

**Purpose**: Handles queries that need external information (web search, news, real-time data) by coordinating with external AI agents.

## 🔄 State Flow: The Shared Clipboard

Throughout this entire process, the **MessagesState** flows like a shared clipboard:

```python
# Initial state
{"messages": [{"role": "user", "content": "Are there vulnerabilities in prod?"}]}

# After supervisor
{"messages": [
    {"role": "user", "content": "Are there vulnerabilities in prod?"},
    {"role": "assistant", "content": "Routing to security...", "name": "supervisor"}
]}

# After security analysis
{"messages": [
    {"role": "user", "content": "Are there vulnerabilities in prod?"},
    {"role": "assistant", "content": "Routing to security...", "name": "supervisor"},
    {"role": "assistant", "content": "Found 3 CVEs requiring attention...", "name": "security_agent"}
]}
```

## 🎯 Why This Architecture is Powerful

### 1. **🧠 Intelligent Routing**
Questions automatically go to the right expert without manual configuration.

### 2. **🔧 Specialized Tools** 
Each domain has tools specific to its expertise:
- **Security**: Vulnerability scanners, approval gates
- **RCA**: Timeline builders, dependency mappers
- **Data**: Graph queries, vector searches

### 3. **📈 Scalable Design**
Adding a new domain (e.g., Cost Optimization) is simple:
```python
# In supervisor.py
workflow.add_node("cost_domain", create_cost_subgraph())

# In routing logic
elif "cost" in user_query or "budget" in user_query:
    return "cost_domain"
```

### 4. **🔒 Enterprise Controls**
- Human-in-the-loop for sensitive operations
- Audit trails through message history
- Role-based access through domain separation

### 5. **🌐 External Integration**
Seamlessly coordinates with external AI systems while maintaining internal workflow control.

## 🚀 Performance Optimizations

### ✅ Agent Lifecycle Management
```python
# CORRECT: Agent created once per subgraph
def create_security_subgraph():
    security_agent = create_react_agent(...)  # Created once
    workflow.add_node("security_agent", security_agent)  # Reused many times

# WRONG: Agent created per invocation (what you fixed)
def bad_security_node(state):
    security_agent = create_react_agent(...)  # Created every time - EXPENSIVE!
```

### ✅ Modular Compilation
Each subgraph compiles independently, allowing for:
- Faster development iterations
- Independent testing
- Parallel execution capabilities

## 🔗 Next: Deep Dive into Subgraph Patterns

Ready to understand the specific patterns used in each subgraph? Continue to: **[03-subgraph-patterns.md](03-subgraph-patterns.md)**
