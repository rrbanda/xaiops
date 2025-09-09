# Contribution Guide: Extending XAI Ops with Confidence

Now that you understand LangGraph concepts and XAI Ops architecture, let's learn how to contribute effectively to the system.

## 🎯 Contribution Philosophy

**XAI Ops follows these principles:**
- 🏗️ **Modular Design**: Each domain is independent and reusable
- 🧠 **Agent Specialization**: Each agent has clear expertise boundaries  
- 🔧 **Tool-First**: Capabilities come from tools, agents orchestrate them
- 📈 **Incremental Enhancement**: Start simple, add complexity gradually
- 🔒 **Enterprise-Ready**: Security, governance, and reliability first

---

## 🚀 Common Contribution Scenarios

### 📋 Scenario 1: Adding a New Domain

**Example**: Adding a "Cost Optimization" domain

#### Step 1: Create the Subgraph
```python
# File: src/app/graphs/domain_subgraphs.py

def create_cost_subgraph():
    """Cost optimization domain with specialized tools"""
    
    # Choose appropriate pattern based on complexity
    # For cost analysis, we'll use Simple RAG pattern
    cost_agent = create_react_agent(
        model=get_llm(),
        tools=[
            neo4j_query_tool,      # Infrastructure cost data
            vector_search_tool,    # Cost optimization patterns
            cost_calculator_tool,  # Custom cost analysis tool
        ],
        prompt=load_prompt("cost_domain"),
        name="cost_agent"
    )
    
    workflow = StateGraph(MessagesState)
    workflow.add_node("cost_agent", cost_agent)
    workflow.add_edge(START, "cost_agent")
    workflow.add_edge("cost_agent", END)
    
    return workflow.compile()
```

#### Step 2: Create Domain Prompt
```markdown
<!-- File: src/app/prompts/cost_domain.md -->

# Cost Optimization Expert

You are a cloud cost optimization specialist analyzing infrastructure expenses.

## Your Responsibilities
1. Analyze cost queries using available tools
2. Identify cost savings opportunities
3. Provide actionable recommendations with ROI estimates
4. Consider both immediate and long-term cost implications

## Tool Usage Guidelines

### neo4j_query_tool
- For infrastructure cost data: `query_type="systems"` with cost-related search terms
- For service costs: `query_type="services"` 
- For historical spending: `query_type="events"` with date ranges

### vector_search_tool  
- Search for cost optimization patterns: "cost reduction cloud optimization"
- Find similar infrastructure setups: "similar deployment cost analysis"
- Research best practices: "cloud cost optimization best practices"

### cost_calculator_tool
- Calculate potential savings: estimate_savings(current_cost, optimization_plan)
- ROI analysis: calculate_roi(investment, annual_savings)

## Response Format
Always provide:
1. Current state analysis
2. Cost savings opportunities  
3. Implementation recommendations
4. Expected ROI and timeline
```

#### Step 3: Integrate into Supervisor
```python
# File: src/app/graphs/supervisor.py

def create_supervisor():
    # Add new domain
    workflow.add_node("cost_domain", create_cost_subgraph())
    
    # Update routing logic
    workflow.add_conditional_edges(
        "supervisor",
        route_query,
        {
            "data_domain": "data_domain",
            "security_domain": "security_domain",
            "rca_domain": "rca_domain", 
            "cost_domain": "cost_domain",  # New domain
            # ... other domains
        }
    )
    
    # Add termination edge
    workflow.add_edge("cost_domain", END)

def route_query(state):
    """Enhanced routing with cost domain"""
    user_query = extract_user_query(state).lower()
    
    # Add cost-related routing
    if any(word in user_query for word in ["cost", "budget", "savings", "expense", "pricing"]):
        return "cost_domain"
    # ... existing routing logic
```

#### Step 4: Create Custom Tools (if needed)
```python
# File: src/app/tools/cost_tools.py

from langchain_core.tools import tool

@tool
def cost_calculator_tool(
    resource_type: str, 
    current_usage: int, 
    optimization_plan: str
) -> str:
    """Calculate cost savings for infrastructure optimization"""
    
    # Cost calculation logic
    base_costs = {
        "vm": 100,  # per month per VM
        "storage": 50,  # per TB per month
        "network": 20   # per GB per month
    }
    
    current_cost = base_costs.get(resource_type, 0) * current_usage
    
    # Optimization calculations based on plan
    if "rightsizing" in optimization_plan.lower():
        savings_percent = 0.30
    elif "reserved instances" in optimization_plan.lower():
        savings_percent = 0.40
    else:
        savings_percent = 0.15
    
    monthly_savings = current_cost * savings_percent
    annual_savings = monthly_savings * 12
    
    return f"""
    Cost Analysis:
    - Current monthly cost: ${current_cost:,.2f}
    - Optimization plan: {optimization_plan}
    - Monthly savings: ${monthly_savings:,.2f}
    - Annual savings: ${annual_savings:,.2f}
    - ROI: {savings_percent:.0%}
    """
```

### 🧪 Testing Your New Domain

```python
# File: tests/test_cost_domain.py

def test_cost_domain_basic():
    """Test basic cost domain functionality"""
    from app.graphs.domain_subgraphs import create_cost_subgraph
    
    cost_graph = create_cost_subgraph()
    
    # Test basic cost query
    response = cost_graph.invoke({
        "messages": [{"role": "user", "content": "What are our monthly cloud costs?"}]
    })
    
    assert "cost" in response["messages"][-1]["content"].lower()
    assert response["messages"][-1]["name"] == "cost_agent"

def test_cost_routing():
    """Test supervisor routes cost queries correctly"""
    from app.graphs.supervisor import create_supervisor, route_query
    
    # Test cost-related keywords
    test_cases = [
        "What are our AWS costs?",
        "How can we reduce our cloud budget?", 
        "Show me cost savings opportunities"
    ]
    
    for query in test_cases:
        state = {"messages": [{"role": "user", "content": query}]}
        route = route_query(state)
        assert route == "cost_domain"
```

---

### 📋 Scenario 2: Enhancing Existing Domain

**Example**: Adding quality control to Data Domain (Proposed Enhancement)

⚠️ **Note**: This is an example of how you could enhance the existing data domain, not current implementation.

#### Step 1: Add Quality Grading (Proposed Enhancement)
```python
# File: src/app/graphs/domain_subgraphs.py
# Status: PROPOSED ENHANCEMENT - Not currently implemented

def create_enhanced_data_subgraph():
    """PROPOSED: Data domain with quality control"""
    
    # Use existing agents from current implementation
    graph_agent = create_react_agent(...)  # Already exists
    vector_agent = create_react_agent(...)  # Already exists
    
    # PROPOSED: Add quality grader
    def grade_retrieval_quality(state):
        """PROPOSED: Grade if retrieved data is sufficient"""
        user_query = extract_user_query(state)
        graph_data = extract_agent_response(state, "graph_collector")
        vector_data = extract_agent_response(state, "context_enhancer")
        
        grader_prompt = f"""
        Query: {user_query}
        Graph data: {graph_data}
        Vector data: {vector_data}
        
        Is this data sufficient to fully answer the query?
        Consider:
        - Completeness: Does it address all aspects?
        - Relevance: Is it directly related to the query?
        - Actionability: Can the user act on this information?
        
        Grade: 'sufficient' or 'insufficient'
        Reason: Brief explanation
        """
        
        response = get_llm().invoke(grader_prompt)
        
        if "sufficient" in response.content.lower():
            return "synthesis"
        else:
            return "refine_query"
    
    # PROPOSED: Query refinement
    def refine_query_node(state):
        """PROPOSED: Improve query for better results"""
        original_query = extract_user_query(state)
        
        refine_prompt = f"""
        The query "{original_query}" didn't return sufficient infrastructure data.
        
        Rewrite it to be more specific:
        - Add specific entity types (servers, databases, applications)
        - Include environment context (production, staging, development)
        - Specify the type of information needed (count, status, configuration)
        
        Improved query:
        """
        
        response = get_llm().invoke(refine_prompt)
        return {"messages": [{"role": "user", "content": response.content}]}
    
    # PROPOSED: Enhanced workflow with quality control
    workflow = StateGraph(MessagesState)
    workflow.add_node("graph_collector", graph_agent)
    workflow.add_node("context_enhancer", vector_agent)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("refine_query", refine_query_node)  # NEW
    
    # Current flow: START → graph_collector → context_enhancer → synthesis → END
    # PROPOSED enhanced flow with quality control:
    workflow.add_edge(START, "graph_collector")
    workflow.add_edge("graph_collector", "context_enhancer")
    
    # PROPOSED: Quality control branch
    workflow.add_conditional_edges(
        "context_enhancer",
        grade_retrieval_quality,  # NEW FUNCTION
        {
            "synthesis": "synthesis",
            "refine_query": "refine_query"  # NEW PATH
        }
    )
    
    # PROPOSED: Refinement loop
    workflow.add_edge("refine_query", "graph_collector")
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()
```

**Current Implementation**: The data domain uses a simple sequential pipeline (graph → vector → synthesis).
**This Enhancement**: Would add quality control and query refinement capabilities.

---

### 📋 Scenario 3: Adding New Tools

**Example**: Adding a monitoring tool for real-time metrics

#### Step 1: Create the Tool
```python
# File: src/app/tools/monitoring_tools.py

import httpx
from langchain_core.tools import tool

@tool
def real_time_metrics_tool(
    metric_type: str,
    resource_name: str, 
    time_range: str = "1h"
) -> str:
    """Get real-time metrics from monitoring system"""
    
    # Mapping metric types to monitoring API endpoints
    metric_endpoints = {
        "cpu": "/api/v1/cpu_usage",
        "memory": "/api/v1/memory_usage", 
        "disk": "/api/v1/disk_usage",
        "network": "/api/v1/network_io"
    }
    
    if metric_type not in metric_endpoints:
        return f"Unsupported metric type: {metric_type}. Supported: {list(metric_endpoints.keys())}"
    
    try:
        # Call monitoring API
        with httpx.Client() as client:
            response = client.get(
                f"http://monitoring-api:8080{metric_endpoints[metric_type]}",
                params={
                    "resource": resource_name,
                    "timerange": time_range
                }
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Format response
            return f"""
            Real-time {metric_type} metrics for {resource_name}:
            - Current value: {data.get('current', 'N/A')}
            - Average ({time_range}): {data.get('average', 'N/A')}
            - Peak ({time_range}): {data.get('peak', 'N/A')}
            - Trend: {data.get('trend', 'stable')}
            """
            
    except Exception as e:
        return f"Error fetching metrics: {str(e)}"

@tool  
def alert_status_tool(severity: str = "all") -> str:
    """Get current alert status from monitoring system"""
    
    try:
        with httpx.Client() as client:
            response = client.get(
                "http://monitoring-api:8080/api/v1/alerts",
                params={"severity": severity}
            )
            response.raise_for_status()
            
            alerts = response.json()
            
            if not alerts:
                return f"No {severity} alerts currently active."
            
            alert_summary = []
            for alert in alerts[:10]:  # Limit to 10 most recent
                alert_summary.append(
                    f"- {alert['resource']}: {alert['message']} (since {alert['started']})"
                )
            
            return f"Current {severity} alerts:\n" + "\n".join(alert_summary)
            
    except Exception as e:
        return f"Error fetching alerts: {str(e)}"
```

#### Step 2: Add Tools to Relevant Domains
```python
# File: src/app/graphs/domain_subgraphs.py

def create_performance_subgraph():
    """Enhanced performance domain with real-time monitoring"""
    
    performance_agent = create_react_agent(
        model=get_llm(),
        tools=[
            neo4j_query_tool,
            vector_search_tool,
            real_time_metrics_tool,    # New tool
            alert_status_tool,         # New tool
            security_approval_gate
        ],
        prompt=load_prompt("performance_domain"),
        name="performance_agent"
    )
    
    workflow = StateGraph(MessagesState)
    workflow.add_node("performance_agent", performance_agent)
    workflow.add_edge(START, "performance_agent")
    workflow.add_edge("performance_agent", END)
    
    return workflow.compile()
```

#### Step 3: Update Domain Prompt
```markdown
<!-- File: src/app/prompts/performance_domain.md -->

# Performance Analysis Expert

You are a performance optimization specialist.

## New Tool: real_time_metrics_tool
Use for current performance data:
- CPU usage: `real_time_metrics_tool(metric_type="cpu", resource_name="web-prod-01")`
- Memory usage: `real_time_metrics_tool(metric_type="memory", resource_name="db-prod-02")`
- Time ranges: "1h", "6h", "24h"

## New Tool: alert_status_tool  
Use for checking current alerts:
- All alerts: `alert_status_tool()`
- Critical only: `alert_status_tool(severity="critical")`

## Analysis Workflow
1. Check alerts first with alert_status_tool
2. Get historical context with neo4j_query_tool
3. Get real-time metrics with real_time_metrics_tool
4. Find patterns with vector_search_tool
5. Provide actionable recommendations
```

---

## 🛠️ Development Best Practices

### ✅ Code Organization

```
src/app/
├── graphs/
│   ├── supervisor.py           # Main orchestration
│   ├── domain_subgraphs.py     # Simple domains  
│   └── specialized_subgraph.py # Complex domains (separate files)
├── tools/
│   ├── data_tools.py          # General data access
│   ├── domain_tools.py        # Domain-specific tools
│   └── integration_tools.py   # External integrations
├── prompts/
│   ├── domain_name.md         # One prompt per domain
│   └── shared_guidelines.md   # Common instructions
└── state.py                   # State definitions
```

### ✅ Testing Strategy

```python
# Unit tests: Test individual components
def test_cost_calculator_tool():
    result = cost_calculator_tool("vm", 10, "rightsizing")
    assert "30%" in result  # Expected savings percentage

# Integration tests: Test subgraph workflows  
def test_cost_subgraph_integration():
    graph = create_cost_subgraph()
    response = graph.invoke(test_input)
    assert response["messages"][-1]["name"] == "cost_agent"

# End-to-end tests: Test complete user journeys
def test_cost_analysis_journey():
    supervisor = create_supervisor()
    response = supervisor.invoke({
        "messages": [{"role": "user", "content": "How can we reduce AWS costs?"}]
    })
    assert "cost" in response["messages"][-1]["content"].lower()
```

### ✅ Error Handling

```python
@tool
def robust_api_tool(endpoint: str) -> str:
    """Tool with proper error handling"""
    try:
        response = call_external_api(endpoint)
        return format_success_response(response)
    except ConnectionError:
        return "External service unavailable. Please try again later."
    except TimeoutError:
        return "Request timed out. The service may be overloaded."
    except Exception as e:
        return f"Unexpected error: {str(e)}. Please contact support."
```

### ✅ Performance Considerations

```python
# DO: Create agents at subgraph level
def create_domain_subgraph():
    agent = create_react_agent(...)  # Created once
    workflow.add_node("agent", agent)

# DO: Use connection pooling for external APIs
@tool
def api_tool():
    with httpx.Client() as client:  # Reuses connections
        return client.get(url)

# DO: Cache expensive operations
@lru_cache(maxsize=128)
def expensive_calculation(params):
    return complex_computation(params)
```

---

## 🚦 Code Review Checklist

### 🔍 Before Submitting

- [ ] **Agent Lifecycle**: Agents created at subgraph level, not in node functions
- [ ] **Error Handling**: All tools handle errors gracefully
- [ ] **Testing**: Unit tests for tools, integration tests for subgraphs
- [ ] **Documentation**: Prompt files updated with new tool usage
- [ ] **Routing**: Supervisor routing updated for new domains
- [ ] **Performance**: No obvious performance bottlenecks
- [ ] **Security**: Sensitive operations use approval gates where needed

### 📋 Code Review Questions

1. **Architecture**: Does this follow established patterns?
2. **Modularity**: Is the new code properly separated and reusable?
3. **Testing**: Are there adequate tests covering the functionality?
4. **Documentation**: Can a new contributor understand this code?
5. **Error Cases**: How does this behave when things go wrong?
6. **Performance**: Will this scale with increased usage?

---

## 🎯 Advanced Contribution Patterns (Potential Enhancements)

⚠️ **Note**: These are potential enhancement patterns, not currently implemented in XAI Ops.

### 🔄 Parallel Processing Enhancement (Proposed)
```python
# Status: POTENTIAL ENHANCEMENT - Not currently implemented
def create_parallel_data_subgraph():
    """PROPOSED: Process graph and vector retrieval in parallel"""
    
    async def parallel_retrieval_node(state):
        """PROPOSED: Run both agents concurrently"""
        tasks = [
            graph_agent.ainvoke(state),
            vector_agent.ainvoke(state)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Combine results
        combined_state = {"messages": state["messages"]}
        for result in results:
            combined_state["messages"].extend(result["messages"])
            
        return combined_state
```

**Current Implementation**: Sequential processing (graph → vector → synthesis)
**This Enhancement**: Would enable parallel processing for faster responses

### 🎛️ Dynamic Tool Selection (Proposed)
```python
# Status: POTENTIAL ENHANCEMENT - Not currently implemented  
def create_adaptive_agent():
    """PROPOSED: Agent that selects tools based on query analysis"""
    
    def tool_selector_node(state):
        """PROPOSED: Analyze query and select appropriate tools"""
        query = extract_user_query(state)
        
        # AI-driven tool selection
        selected_tools = analyze_and_select_tools(query)
        
        # Create agent with selected tools
        adaptive_agent = create_react_agent(
            model=get_llm(),
            tools=selected_tools,
            prompt=get_adaptive_prompt(selected_tools)
        )
        
        return adaptive_agent.invoke(state)
```

**Current Implementation**: Fixed tool sets per domain
**This Enhancement**: Would enable dynamic tool selection based on query analysis

---

## 🚀 Ready to Contribute!

You now have comprehensive understanding of:
- ✅ **LangGraph concepts** and real-world analogies
- ✅ **XAI Ops architecture** and design patterns  
- ✅ **Subgraph patterns** and when to use each
- ✅ **Agent lifecycle** and performance optimization
- ✅ **RAG patterns** from simple to sophisticated
- ✅ **Contribution patterns** for extending the system

### 🎯 Next Steps

1. **Start Small**: Add a simple tool to an existing domain
2. **Build Confidence**: Implement a new simple domain using existing patterns
3. **Scale Up**: Design complex multi-agent workflows
4. **Innovate**: Create new patterns for novel use cases

### 🤝 Getting Help

- **Code Questions**: Review existing implementations for patterns
- **Architecture Questions**: Refer back to concept explanations
- **Performance Issues**: Check agent lifecycle and creation patterns
- **New Patterns**: Start with simple approaches and enhance incrementally

**Happy Contributing! 🎉**
