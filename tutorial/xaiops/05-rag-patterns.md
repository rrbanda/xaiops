# RAG Patterns: From Simple to Sophisticated

XAI Ops implements multiple RAG (Retrieval-Augmented Generation) patterns, from simple single-agent RAG to sophisticated hybrid multi-source RAG. Understanding these patterns is key to extending the system's data capabilities.

## 🧬 RAG Evolution in XAI Ops

```
Simple RAG → Agentic RAG → Hybrid RAG → Multi-Domain RAG
    ⭐           ⭐⭐            ⭐⭐⭐           ⭐⭐⭐⭐
```

---

## 📚 RAG Pattern 1: Simple Agent RAG

**Used in**: Security, Performance, Compliance domains
**Pattern**: Single agent with dual tools

### 🏗️ Implementation
```python
def create_security_subgraph():
    """Simple RAG: One agent, two retrieval tools"""
    security_agent = create_react_agent(
        model=get_llm(),
        tools=[
            neo4j_query_tool,     # Structured retrieval
            vector_search_tool    # Semantic retrieval
        ],
        prompt=load_prompt("security_domain"),
        name="security_agent"
    )
```

### 🔄 How It Works
```
User: "What security vulnerabilities exist in production?"

Agent's RAG Process:
1. 🤔 Analyze: "This needs both structured and semantic data"
2. 🗄️ Retrieve: neo4j_query_tool(query_type="vulnerabilities", search_term="production")
   → Structured: "CVE-2024-1234 affects nginx v1.18, CVE-2024-5678 affects openssl"
3. 🔍 Retrieve: vector_search_tool(query="production security vulnerabilities")  
   → Semantic: "Similar patterns show these CVEs cluster around web services"
4. 🎯 Generate: "Found 2 critical CVEs in production. CVE-2024-1234 affects nginx..."
```

### ✅ Advantages
- Simple to implement and understand
- Agent intelligently decides which tool to use when
- Good for domains where one expert can handle complexity

### ❌ Limitations  
- Single perspective (one agent's reasoning)
- No specialization between retrieval types
- Limited synthesis capabilities

---

## 🤖 RAG Pattern 2: Agentic RAG (Not Currently Implemented)

**Reference**: [LangGraph Agentic RAG Tutorial](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/)
**Status**: ⚠️ **POTENTIAL ENHANCEMENT** - Not currently implemented in XAI Ops

This pattern adds quality control and query refinement to RAG systems. While not currently implemented in XAI Ops, it could be valuable for future enhancements.

### 🔄 How Agentic RAG Would Work
```
Query: "Server issues"  (vague query)

Potential Flow:
1. query_or_respond → Decides to retrieve
2. retrieve → Gets documents about servers
3. grade_documents → "Documents too generic, score: no"
4. rewrite_question → "What specific server performance issues exist in production?"
5. query_or_respond → Retrieves with better query
6. grade_documents → "Relevant documents, score: yes"  
7. generate_answer → High-quality response
```

### 💡 Potential Benefits for XAI Ops
- Quality control through result grading
- Query refinement for better infrastructure queries
- Adaptive behavior based on retrieval quality

**Note**: This is a potential enhancement pattern, not currently implemented.

---

## 🏭 RAG Pattern 3: Hybrid Dual-Source RAG (Current Implementation)

**Used in**: Data Domain  
**Pattern**: Sequential specialized agents + synthesis
**Status**: ✅ **CURRENTLY IMPLEMENTED** in XAI Ops

### 🏗️ Implementation
```python
def create_data_subgraph():
    """Hybrid RAG: Graph + Vector + Synthesis"""
    
    # Agent 1: Structured data specialist
    graph_agent = create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool],
        prompt="""You are a database expert analyzing infrastructure queries.
        
        Use neo4j_query_tool to get precise, structured data:
        - For servers/infrastructure → query_type="systems"
        - For applications/services → query_type="services"  
        - For security issues → query_type="vulnerabilities"
        
        Return clean, factual data from the knowledge graph.""",
        name="graph_collector"
    )
    
    # Agent 2: Semantic pattern specialist  
    vector_agent = create_react_agent(
        model=get_llm(),
        tools=[vector_search_tool],
        prompt="""You are a semantic search expert for infrastructure patterns.
        
        Use vector_search_tool to find:
        - Similar configurations and setups
        - Related patterns and contexts
        - Historical operational insights
        
        Focus on patterns that complement structured data analysis.""",
        name="context_enhancer"
    )
    
    # Function 3: Intelligent synthesis
    def synthesis_node(state):
        """Combine graph + vector insights intelligently"""
        graph_data = extract_agent_response(state, "graph_collector")
        vector_data = extract_agent_response(state, "context_enhancer")
        
        synthesis_prompt = f"""
        PRIMARY DATA (structured from knowledge graph):
        {graph_data}
        
        CONTEXTUAL INSIGHTS (patterns from vector search):  
        {vector_data}
        
        Create a comprehensive response that:
        1. Directly answers using primary data
        2. Adds relevant context and patterns
        3. Provides actionable insights
        """
        
        response = get_llm().invoke(synthesis_prompt)
        return {"messages": [{"role": "assistant", "content": response.content}]}
    
    # Sequential pipeline
    workflow = StateGraph(MessagesState)
    workflow.add_node("graph_collector", graph_agent)
    workflow.add_node("context_enhancer", vector_agent)  
    workflow.add_node("synthesis", synthesis_node)
    
    workflow.add_edge(START, "graph_collector")
    workflow.add_edge("graph_collector", "context_enhancer")
    workflow.add_edge("context_enhancer", "synthesis")
    workflow.add_edge("synthesis", END)
```

### 🔄 Hybrid RAG Flow
```
Query: "How many database servers are running and are they properly configured?"

Stage 1 - Graph Collection (Structured):
├─ Agent analyzes: "Need systems query for databases"
├─ neo4j_query_tool(query_type="systems", search_term="database")
└─ Output: "12 database servers: db-prod-01 (MySQL 8.0), db-prod-02 (PostgreSQL 13)..."

Stage 2 - Context Enhancement (Semantic):
├─ Agent analyzes: "Find patterns for database configurations"  
├─ vector_search_tool(query="database server configuration best practices")
└─ Output: "Similar setups use master-slave replication, automated backups at 2 AM..."

Stage 3 - Synthesis (Intelligence):
├─ Combines: Factual inventory + Best practice patterns
└─ Output: "You have 12 database servers running. Analysis shows:
            - Current state: Mix of MySQL and PostgreSQL
            - Configuration: Follows recommended master-slave pattern
            - Recommendation: Consider upgrading MySQL 5.7 instances to 8.0"
```

### 🏆 Why This Pattern is Superior

#### vs Simple RAG:
- ✅ **Dual expertise**: Database expert + Pattern expert vs single agent
- ✅ **Specialized retrieval**: Optimized queries for each data type
- ✅ **Synthesis layer**: Intelligent combination vs single perspective

#### vs Agentic RAG:  
- ✅ **Dual data sources**: Graph + Vector vs single vector store
- ✅ **Domain specialization**: Infrastructure-specific vs generic
- ✅ **Richer context**: Structured relationships + semantic patterns

#### vs Basic Multi-Agent:
- ✅ **Coordinated pipeline**: Sequential specialization vs parallel chaos
- ✅ **Synthesis intelligence**: Dedicated combination logic vs hoping agents coordinate

---

## 🌐 RAG Pattern 4: Multi-Domain RAG (System Architecture)

**Used in**: Entire XAI Ops system
**Pattern**: Domain-specialized RAG systems with intelligent routing  
**Status**: ✅ **CURRENTLY IMPLEMENTED** in XAI Ops

### 🏗️ System-Level Implementation
```python
def create_supervisor():
    """Multi-domain RAG orchestrator"""
    
    # Domain-specific RAG systems
    workflow.add_node("data_domain", create_data_subgraph())          # Hybrid RAG
    workflow.add_node("security_domain", create_security_subgraph())  # Simple RAG
    workflow.add_node("rca_domain", create_rca_subgraph())           # Tool-enhanced RAG
    
    # Intelligent routing to appropriate RAG system
    workflow.add_conditional_edges("supervisor", route_query, {
        "data_domain": "data_domain",
        "security_domain": "security_domain", 
        "rca_domain": "rca_domain"
    })
```

### 🔄 Multi-Domain RAG Flow
```
Query: "Are there any security vulnerabilities in our production databases?"

Routing Intelligence:
├─ Keywords detected: ["security", "vulnerabilities", "production", "databases"]
├─ Domain analysis: Security + Data hybrid query
└─ Routing decision: "security_domain" (security takes priority)

Security Domain RAG:
├─ neo4j_query_tool(query_type="vulnerabilities", search_term="database production")
├─ vector_search_tool(query="database security vulnerabilities production")
├─ security_approval_gate(findings="2 CVEs found", action="report")
└─ Response: "Found 2 database vulnerabilities requiring immediate attention..."
```

### 🏆 Enterprise RAG Benefits
- **🎯 Domain expertise**: Each RAG system optimized for its domain
- **🚦 Smart routing**: Queries automatically go to best RAG system  
- **🔧 Specialized tools**: Each domain has relevant retrieval tools
- **📈 Scalable**: Easy to add new domain RAG systems
- **🔒 Governance**: Domain-specific controls (e.g., security approval)

---

## 📊 RAG Pattern Comparison

| Pattern | Complexity | Data Sources | Agents | Use Case |
|---------|------------|-------------|---------|----------|
| **Simple RAG** | ⭐ | 1-2 | 1 | Single domain expertise |
| **Agentic RAG** | ⭐⭐ | 1 | 1 + Quality control | Generic Q&A with refinement |
| **Hybrid RAG** | ⭐⭐⭐ | 2 (Graph + Vector) | 2 + Synthesis | Infrastructure analysis |
| **Multi-Domain RAG** | ⭐⭐⭐⭐ | Multiple per domain | Multiple | Enterprise AI system |

## 🎯 When to Use Each Pattern

### 🤔 Decision Tree
```
New retrieval requirement:
├─ Single domain, simple queries? → Simple RAG
├─ Need quality control and refinement? → Agentic RAG  
├─ Complex domain with multiple data sources? → Hybrid RAG
└─ Multiple domains with specialized needs? → Multi-Domain RAG
```

### 📈 Pattern Evolution Path
```
Start: Simple RAG
  ↓ (need quality control)
Enhance: Add Agentic RAG elements  
  ↓ (need multiple data sources)
Upgrade: Implement Hybrid RAG
  ↓ (need multiple domains)
Scale: Build Multi-Domain RAG
```

## 🛠️ RAG Development Best Practices

### ✅ DO: Match Pattern to Complexity
```python
# Simple domain → Simple RAG
security_agent = create_react_agent(tools=[neo4j_tool, vector_tool])

# Complex domain → Hybrid RAG  
data_subgraph = create_sequential_pipeline(graph_agent, vector_agent, synthesis)
```

### ✅ DO: Specialize Agent Prompts
```python
# Graph agent prompt
"You are a database expert. Use neo4j_query_tool for precise infrastructure data."

# Vector agent prompt  
"You are a pattern analyst. Use vector_search_tool for operational insights."
```

### ✅ DO: Implement Intelligent Synthesis
```python
def synthesis_node(state):
    """Don't just concatenate - intelligently combine"""
    graph_data = extract_structured_data(state)
    vector_data = extract_patterns(state)
    
    # Add business logic for combination
    if graph_data.count > 0 and vector_data.has_patterns:
        return create_comprehensive_response(graph_data, vector_data)
    elif graph_data.count == 0:
        return suggest_alternatives(vector_data)
    else:
        return structured_response_only(graph_data)
```

### ❌ DON'T: Over-Engineer Simple Domains
```python
# DON'T use Hybrid RAG for simple lookup queries
# Use Simple RAG instead
```

### ❌ DON'T: Under-Engineer Complex Domains
```python
# DON'T use Simple RAG for complex infrastructure analysis
# Use Hybrid or Multi-Domain RAG instead
```

---

## 🔗 Next: Contributing to the System

Ready to start contributing? Learn how to extend XAI Ops: **[06-contribution-guide.md](06-contribution-guide.md)**
