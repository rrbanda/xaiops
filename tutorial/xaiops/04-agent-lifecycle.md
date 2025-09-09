# Agent Lifecycle: Creation, Management, and Best Practices

Understanding how agents are created and managed is crucial for contributing to XAI Ops. This tutorial covers the agent lifecycle and the correct patterns implemented in the codebase.

## 🔄 The Agent Lifecycle Journey

```
📝 Agent Definition → 🏗️ Creation → 📦 Compilation → 🚀 Execution → ♻️ Reuse
```

---

## 🏗️ Agent Creation: The Correct Pattern

### ✅ XAI Ops Implementation: Subgraph-Level Creation

**Current implementation** in `domain_subgraphs.py`:
```python
def create_data_subgraph():
    """Create agents ONCE at subgraph compilation time"""
    
    # ✅ BEST PRACTICE: Create agents at subgraph level
    graph_agent = create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool],
        prompt="You are a database expert...",
        name="graph_collector"
    )
    
    vector_agent = create_react_agent(
        model=get_llm(),
        tools=[vector_search_tool], 
        prompt="You are a semantic search expert...",
        name="context_enhancer"
    )
    
    # Add agents as nodes for reuse
    workflow = StateGraph(MessagesState)
    workflow.add_node("graph_collector", graph_agent)
    workflow.add_node("context_enhancer", vector_agent)
    
    return workflow.compile()  # Agents become part of compiled graph
```

**How it works**:
```
Startup: Creates Agent Instances → Compiles into graph
Query 1: "How many servers?" → Reuses Agent Instances → Fast response
Query 2: "Show databases"   → Reuses Agent Instances → Fast response
Query 3: "List services"    → Reuses Agent Instances → Fast response
```

**Benefits of this approach**:
- ⚡ **Fast performance**: No initialization overhead per call
- 💾 **Memory efficient**: Single agent instance per subgraph
- 🔄 **Consistent behavior**: Same agent handles all requests
- 📏 **LangGraph best practice**: Follows official patterns

### ❌ Anti-Pattern: Avoid Creating Agents in Node Functions

**Don't do this** (performance killer):
```python
def bad_node_function(state):
    # ❌ Creates new agent every time node executes
    agent = create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool],
        prompt="...",
        name="agent"
    )
    return agent.invoke(state)  # Expensive recreation every call
```

This pattern creates unnecessary overhead and should be avoided.

---

## 🧠 Understanding create_react_agent()

### 🔍 What It Actually Creates

```python
agent = create_react_agent(
    model=get_llm(),                    # 🧠 The "brain" (LLM)
    tools=[neo4j_query_tool],          # 🔧 The "hands" (available tools)
    prompt="You are a database expert", # 📚 The "training" (system prompt)
    name="graph_collector"             # 🏷️ The "identity" (for tracing)
)

# What you get back:
# - A callable function that implements ReAct (Reasoning + Acting) pattern
# - Can reason about problems and decide which tools to use
# - Maintains conversation context within a single invocation
# - Stateless between invocations (perfect for reuse)
```

### 🤖 ReAct Pattern in Action

When you call an agent, it follows the **ReAct pattern**:

```
User Query: "How many production databases are there?"

Agent's Internal Process:
1. 🤔 REASON: "This is asking for a count of database systems in production"
2. 🎯 ACT: Call neo4j_query_tool(query_type="systems", search_term="database production")  
3. 🤔 REASON: "I got results showing 8 database servers"
4. 🎯 ACT: Format response with the count and details
5. 📝 RESPOND: "There are 8 production databases: db-prod-01, db-prod-02..."
```

### 🔧 Agent Components Deep Dive

#### The Model (Brain)
```python
model=get_llm()  # Usually Claude or GPT-4
```
- **Purpose**: Reasoning and decision-making
- **Capabilities**: Understanding context, planning tool usage, generating responses
- **Stateless**: No memory between separate invocations

#### The Tools (Hands)
```python
tools=[neo4j_query_tool, vector_search_tool]
```
- **Purpose**: Interface with external systems
- **Agent decides**: Which tool to use, what parameters to pass
- **Results flow**: Tool outputs become part of agent's reasoning

#### The Prompt (Training)
```python
prompt=load_prompt("security_domain")  # From src/app/prompts/security_domain.md
```
- **Purpose**: Domain expertise and behavior guidelines
- **Contains**: Role definition, tool usage guidelines, output format
- **Example**: "You are a security expert. Use neo4j_query_tool for vulnerability data..."

#### The Name (Identity)
```python
name="security_agent"
```
- **Purpose**: Tracing and debugging
- **Shows up in**: LangSmith traces, message metadata, logs
- **Helps with**: Understanding which agent generated which response

---

## 🏛️ Agent Architecture Patterns

### 🎯 Pattern 1: Specialized Single Agent
**Used in**: Security, Performance, Compliance
```python
def create_security_subgraph():
    # One expert agent with domain-specific tools
    security_agent = create_react_agent(
        model=get_llm(),
        tools=[neo4j_query_tool, vector_search_tool, security_approval_gate],
        prompt=load_prompt("security_domain"),
        name="security_agent"
    )
    
    # Agent handles all security-related complexity
    workflow.add_node("security_agent", security_agent)
```

**When to use**: Domain has clear boundaries and one expert can handle all scenarios.

### 🏭 Pattern 2: Multi-Agent Pipeline  
**Used in**: Data Domain
```python
def create_data_subgraph():
    # Multiple specialized agents
    graph_agent = create_react_agent(...)     # Database expert
    vector_agent = create_react_agent(...)    # Search expert
    
    # Each agent has specific expertise
    workflow.add_node("graph_collector", graph_agent)
    workflow.add_node("context_enhancer", vector_agent)
```

**When to use**: Complex domain requiring different types of expertise.

### 🔧 Pattern 3: Tool-Heavy Agent
**Used in**: RCA Domain  
```python
def create_rca_subgraph():
    # One agent with many specialized tools
    rca_agent = create_react_agent(
        model=get_llm(),
        tools=[
            discover_incidents,
            rca_timeline_query,
            dependency_traversal_query,
            similarity_search_analysis,
            neo4j_query_tool,
            vector_search_tool
        ],
        prompt=load_prompt("rca_domain"),
        name="rca_agent"
    )
```

**When to use**: Domain has complex methodology requiring orchestrated tool usage.

---

## 🔬 Agent State Management

### 📝 Important: Agents Are Stateless Between Calls

```python
# Each invocation is independent
response1 = security_agent.invoke({"messages": [{"role": "user", "content": "Check vulnerabilities"}]})
response2 = security_agent.invoke({"messages": [{"role": "user", "content": "What did you find?"}]})

# response2 has NO MEMORY of response1!
# The agent doesn't remember previous conversations
```

### 🧠 State Lives in the Graph, Not the Agent

```python
# Graph-level state persists across nodes
state = {
    "messages": [
        {"role": "user", "content": "Check vulnerabilities"},
        {"role": "assistant", "content": "Found 3 CVEs", "name": "security_agent"},
        {"role": "assistant", "content": "Analyzing patterns...", "name": "vector_agent"}
    ]
}

# Each agent sees the full conversation history in state["messages"]
```

### 🔄 How Memory Works in Multi-Node Flows

```python
# In data subgraph:
1. graph_agent.invoke(state)     # Sees: [user_query]
   → Adds: [user_query, graph_response]

2. vector_agent.invoke(state)    # Sees: [user_query, graph_response]  
   → Adds: [user_query, graph_response, vector_response]

3. synthesis_node(state)         # Sees: [user_query, graph_response, vector_response]
   → Combines all information
```

---

## 🛠️ Agent Development Best Practices

### ✅ DO: Create Agents at Subgraph Level
```python
def create_domain_subgraph():
    agent = create_react_agent(...)  # ✅ Created once
    workflow.add_node("agent", agent)
    return workflow.compile()
```

### ❌ DON'T: Create Agents in Node Functions
```python
def domain_node(state):
    agent = create_react_agent(...)  # ❌ Created every time
    return agent.invoke(state)
```

### ✅ DO: Use Descriptive Agent Names
```python
create_react_agent(name="rca_incident_analyzer")  # ✅ Clear purpose
create_react_agent(name="security_vulnerability_scanner")  # ✅ Specific role
```

### ❌ DON'T: Use Generic Names
```python
create_react_agent(name="agent1")  # ❌ Unclear purpose
create_react_agent(name="helper")   # ❌ Too vague
```

### ✅ DO: Provide Domain-Specific Prompts
```python
prompt = """
You are a security expert specializing in infrastructure vulnerabilities.

Your responsibilities:
1. Analyze security queries using available tools
2. Prioritize findings by severity
3. Always use security_approval_gate for sensitive findings
4. Provide actionable recommendations

Guidelines:
- For CVE queries: Use neo4j_query_tool with query_type="vulnerabilities"
- For pattern analysis: Use vector_search_tool
- For any findings: Require human approval via security_approval_gate
"""
```

### ❌ DON'T: Use Generic Prompts
```python
prompt = "You are a helpful assistant."  # ❌ Too generic
```

---

## 🔍 Debugging Agent Issues

### 🕵️ Common Problems and Solutions

#### Problem: Agent Not Using Tools
```python
# Check: Are tools properly added?
tools=[neo4j_query_tool, vector_search_tool]  # ✅ List of tool functions

# Not:
tools="neo4j_query_tool"  # ❌ String instead of function
```

#### Problem: Agent Giving Generic Responses
```python
# Check: Is the prompt specific enough?
prompt=load_prompt("security_domain")  # ✅ Domain-specific training

# Check: Are examples provided in the prompt?
prompt="""
You are a security expert.

Example interaction:
User: "Check for vulnerabilities" 
You: I'll search for vulnerabilities using neo4j_query_tool(query_type="vulnerabilities")
"""
```

#### Problem: Agent Not Accessible
```python
# Check: Is agent added to workflow correctly?
workflow.add_node("security_agent", security_agent)  # ✅ Agent as node

# Not:
workflow.add_node("security_agent", "security_agent")  # ❌ String instead of agent
```

### 📊 Agent Performance Monitoring

```python
# In your prompts, you can add:
"""
Always end your responses with metadata:
- Confidence: High/Medium/Low  
- Tools used: [list of tools]
- Processing time: [if relevant]
"""
```

---

## 🔗 Next: Understanding RAG Patterns

Now let's explore the sophisticated RAG patterns implemented in XAI Ops: **[05-rag-patterns.md](05-rag-patterns.md)**
