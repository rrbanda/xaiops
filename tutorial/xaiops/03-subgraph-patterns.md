# Subgraph Patterns: Design Patterns in Action

XAI Ops implements several sophisticated subgraph patterns. Understanding these patterns will help you extend the system and contribute effectively.

## 🎭 Pattern Overview

| Pattern | Used In | Purpose | Complexity |
|---------|---------|---------|------------|
| **Single Agent** | Security, Performance, Compliance | Simple domain expertise | ⭐⭐ |
| **Sequential Pipeline** | Data Domain | Multi-step data processing | ⭐⭐⭐ |
| **Tool-Enhanced Agent** | RCA, Learning | Specialized tool coordination | ⭐⭐⭐ |
| **External Integration** | A2A Orchestrator | External system coordination | ⭐⭐⭐⭐ |

---

## 🔄 Pattern 1: Single Agent Pattern

**Used in**: Security, Performance, Compliance domains
**File**: `src/app/graphs/domain_subgraphs.py`

### 🏗️ Structure
```python
def create_security_subgraph():
    """Simple but powerful: one expert, multiple tools"""
    workflow = StateGraph(MessagesState)
    
    # One expert agent with domain-specific tools
    security_agent = create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool, vector_search_tool, security_approval_gate],
        prompt=load_prompt("security_domain"),  # Domain expertise
        name="security_agent"
    )
    
    # Simple linear flow
    workflow.add_node("security_agent", security_agent)
    workflow.add_edge(START, "security_agent")
    workflow.add_edge("security_agent", END)
    
    return workflow.compile()
```

### 🎯 When to Use This Pattern
- ✅ **Single domain expertise** (security, performance, compliance)
- ✅ **Agent can handle complexity** with its tools
- ✅ **No need for multi-step coordination**
- ✅ **Human-in-the-loop controls** needed

### 🧠 How the Agent Thinks
```
User: "What security vulnerabilities exist in production?"

Agent's internal reasoning:
1. "This is about vulnerabilities, I should check the database"
2. Uses neo4j_query_tool(query_type="vulnerabilities", search_term="production")
3. "Let me also search for similar vulnerability patterns"
4. Uses vector_search_tool(query="production vulnerability patterns")
5. "This is sensitive security data, I need approval"
6. Uses security_approval_gate(findings="3 CVEs found", action="report")
7. Provides comprehensive security report with human approval
```

### 🔧 Tools in Action
- **neo4j_query_tool**: Structured security data from knowledge graph
- **vector_search_tool**: Similar vulnerability patterns and contexts
- **security_approval_gate**: Human oversight for sensitive findings

---

## 🏭 Pattern 2: Sequential Pipeline Pattern

**Used in**: Data Domain (Graph → Vector → Synthesis)
**File**: `src/app/graphs/domain_subgraphs.py`

### 🏗️ Structure
```python
def create_data_subgraph():
    """Sophisticated pipeline: specialized agents + synthesis"""
    
    # Stage 1: Structured data expert
    graph_agent = create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool],
        prompt="You are a database expert...",
        name="graph_collector"
    )
    
    # Stage 2: Pattern analysis expert  
    vector_agent = create_react_agent(
        model=get_llm(),
        tools=[vector_search_tool],
        prompt="You are a semantic search expert...",
        name="context_enhancer"
    )
    
    # Stage 3: Synthesis function (not an agent)
    def synthesis_node(state):
        """Combine results from both agents"""
        graph_data = extract_agent_response(state, "graph_collector")
        vector_data = extract_agent_response(state, "context_enhancer")
        return intelligent_synthesis(graph_data, vector_data)
    
    # Sequential assembly line
    workflow = StateGraph(MessagesState)
    workflow.add_node("graph_collector", graph_agent)
    workflow.add_node("context_enhancer", vector_agent)
    workflow.add_node("synthesis", synthesis_node)
    
    # Linear flow: Stage 1 → Stage 2 → Stage 3
    workflow.add_edge(START, "graph_collector")
    workflow.add_edge("graph_collector", "context_enhancer")  
    workflow.add_edge("context_enhancer", "synthesis")
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()
```

### 🔄 Pipeline Flow
```
Query: "How many database servers are running?"

Stage 1 - Graph Collector:
├─ Agent analyzes: "This needs 'systems' query for databases"
├─ Tool call: neo4j_query_tool(query_type="systems", search_term="database")
└─ Output: "Found 12 database servers: db-prod-01, db-prod-02..."

Stage 2 - Context Enhancer:
├─ Agent analyzes: "Let me find patterns for database configurations"
├─ Tool call: vector_search_tool(query="database server configuration production")
└─ Output: "Similar setups show master-slave replication, backup schedules..."

Stage 3 - Synthesis:
├─ Combines: Structured data + contextual patterns
└─ Output: "You have 12 database servers in production. Based on analysis,
            they follow master-slave pattern with automated backups..."
```

### 🎯 When to Use This Pattern
- ✅ **Multiple data sources** need coordination
- ✅ **Each stage has clear responsibility**
- ✅ **Final synthesis** adds value beyond individual results
- ✅ **Hybrid RAG** (graph + vector) requirements

### 💡 Why Not Just One Agent?
You could use one agent with both tools, but the pipeline pattern provides:
- **Specialization**: Each agent is an expert in their domain
- **Reliability**: Clearer error handling at each stage
- **Modularity**: Easy to modify or extend individual stages
- **Performance**: Potential for parallel execution (future enhancement)

---

## 🔧 Pattern 3: Tool-Enhanced Agent Pattern

**Used in**: RCA Domain, Learning Domain
**File**: `src/app/graphs/rca_subgraph.py`

### 🏗️ Structure
```python
def create_rca_subgraph():
    """Agent with specialized RCA methodology tools"""
    rca_agent = create_react_agent(
        model=get_llm(),
        tools=[
            # Specialized RCA tools
            discover_incidents,              # Find related incidents
            rca_timeline_query,             # Build incident timeline
            dependency_traversal_query,     # Map system dependencies  
            similarity_search_analysis,     # Find similar past incidents
            # General tools
            neo4j_query_tool,              # Database access
            vector_search_tool             # Pattern search
        ],
        prompt=load_prompt("rca_domain"),   # RCA methodology training
        name="rca_agent"
    )
    
    # Simple wrapper - the intelligence is in the agent + tools
    workflow = StateGraph(MessagesState) 
    workflow.add_node("rca_agent", rca_agent)
    workflow.add_edge(START, "rca_agent")
    workflow.add_edge("rca_agent", END)
    
    return workflow.compile()
```

### 🕵️ RCA Investigation Flow
```
Query: "What caused the API outage yesterday at 2 PM?"

Agent's investigation process:
1. discover_incidents("API outage yesterday 2 PM")
   → Finds: "incident-id-123: API Gateway timeout"

2. rca_timeline_query("incident-id-123") 
   → Timeline: "14:00 - High traffic, 14:05 - Gateway timeout, 14:10 - Service restart"

3. dependency_traversal_query("API Gateway")
   → Dependencies: "API Gateway → Load Balancer → Web Servers → Database"

4. similarity_search_analysis("API Gateway timeout")
   → Similar incidents: "3 similar timeouts in past month, all during peak traffic"

5. neo4j_query_tool(query_type="events", search_term="API Gateway 2 PM")
   → Additional context: "Traffic spike, memory exhaustion logs"

6. Synthesis: "Root cause: API Gateway memory exhaustion under high traffic.
              Recommendation: Increase memory allocation, implement auto-scaling."
```

### 🎯 When to Use This Pattern
- ✅ **Complex domain methodology** (RCA, learning, analysis)
- ✅ **Specialized tools** that work together
- ✅ **Agent needs to orchestrate** multiple tools intelligently
- ✅ **Domain expertise** is primarily in tool usage patterns

### 🔧 Tool Categories
- **Discovery Tools**: `discover_incidents`, `similarity_search_analysis`
- **Analysis Tools**: `rca_timeline_query`, `dependency_traversal_query`
- **General Tools**: `neo4j_query_tool`, `vector_search_tool`

---

## 🌐 Pattern 4: External Integration Pattern

**Used in**: A2A Orchestrator Domain
**File**: `src/app/graphs/a2a_orchestrator_subgraph.py`

### 🏗️ Structure
```python
def create_a2a_orchestrator_subgraph():
    """External AI system coordination"""
    
    async def a2a_orchestrator_node(state):
        """Bridge to external AI agents"""
        original_query = extract_user_query(state)
        
        try:
            # Create A2A protocol request
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "message/send",
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": original_query}]
                    }
                }
            }
            
            # Call external orchestrator and handle async response
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post("http://localhost:8000", json=payload)
                result = await wait_for_task_completion(client, response)
                
                return {
                    "messages": [{
                        "role": "assistant",
                        "content": f"External Agent Response:\n\n{result}",
                        "name": "a2a_orchestrator"
                    }]
                }
                
        except Exception as e:
            return handle_external_error(e)
    
    # Async workflow wrapper
    workflow = StateGraph(MessagesState)
    workflow.add_node("a2a_orchestrator", a2a_orchestrator_node)
    workflow.add_edge(START, "a2a_orchestrator")
    workflow.add_edge("a2a_orchestrator", END)
    
    return workflow.compile()
```

### 🔄 External Coordination Flow
```
Query: "What's the latest news about Kubernetes security?"

Internal Process:
1. Recognize this needs external web search
2. Create A2A JSON-RPC request
3. Send to external AI orchestrator (localhost:8000)
4. External orchestrator coordinates with:
   ├─ Web search agent (localhost:8002)
   └─ LlamaStack agent for analysis
5. Wait for task completion with polling
6. Parse and return structured response

Response: "Latest Kubernetes security news: CVE-2024-XXX discovered,
          patch available in version 1.28.3, affects pod security..."
```

### 🎯 When to Use This Pattern
- ✅ **External AI systems** coordination needed
- ✅ **Real-time data** (web search, news, APIs)
- ✅ **Async operations** with task polling
- ✅ **Protocol bridging** (internal LangGraph ↔ external A2A)

### ⚡ Key Features
- **Async/Await**: Handles long-running external operations
- **Task Polling**: Waits for external task completion
- **Error Handling**: Graceful fallbacks for external failures
- **Protocol Translation**: LangGraph MessagesState ↔ A2A JSON-RPC

---

## 🎯 Pattern Selection Guide

### 🤔 Which Pattern Should I Use?

```
New Domain Requirements:
├─ Simple domain with existing tools? → Single Agent Pattern
├─ Need multiple data sources combined? → Sequential Pipeline Pattern  
├─ Complex methodology with specialized tools? → Tool-Enhanced Agent Pattern
└─ External system integration needed? → External Integration Pattern
```

### 📊 Pattern Comparison

| Aspect | Single Agent | Pipeline | Tool-Enhanced | External |
|--------|-------------|----------|---------------|----------|
| **Complexity** | Low | Medium | Medium | High |
| **Tool Count** | 2-4 | 2-3 per stage | 5+ | N/A |
| **Coordination** | None | Sequential | Intelligent | Async |
| **Error Handling** | Simple | Per-stage | Agent-managed | Distributed |
| **Performance** | Fast | Medium | Medium | Variable |
| **Extensibility** | Easy | Modular | Tool-focused | Protocol-bound |

## 🔗 Next: Understanding Agent Lifecycle

Now let's dive deep into how agents are created and managed: **[04-agent-lifecycle.md](04-agent-lifecycle.md)**
