# XAI Ops LangGraph Quick Reference

*Use this as a quick lookup while working with the codebase*

## 🏗️ Core LangGraph Concepts

| Concept | Purpose | XAI Ops Example |
|---------|---------|-----------------|
| **Graph** | Workflow orchestrator | `supervisor.py` - routes queries |
| **Node** | Work performer | Agents + synthesis functions |
| **Edge** | Flow controller | Routing logic between domains |
| **State** | Shared memory | `MessagesState` - conversation history |
| **Subgraph** | Reusable workflow | Each domain (security, data, RCA) |
| **Agent** | Smart decision maker | Domain experts with tools |

## 🎭 Subgraph Patterns

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Single Agent** | Simple domain | Security, Performance |
| **Sequential Pipeline** | Multi-step processing | Data Domain (Graph→Vector→Synthesis) |
| **Tool-Enhanced** | Complex methodology | RCA with specialized tools |
| **External Integration** | Outside system calls | A2A Orchestrator |

## 🤖 Agent Creation Best Practice

### ✅ Correct Pattern (Used in XAI Ops)
```python
def create_domain_subgraph():
    agent = create_react_agent(...)  # Create once at subgraph level
    workflow.add_node("agent", agent)  # Reuse for all calls
    return workflow.compile()
```

### ❌ Anti-Pattern (Avoid This)
```python
def domain_node(state):
    agent = create_react_agent(...)  # Performance overhead!
    return agent.invoke(state)
```

## 🔄 RAG Pattern Selection

| Need | Pattern | Implementation |
|------|---------|----------------|
| Simple retrieval | **Simple RAG** | One agent, 1-2 tools |
| Multiple data sources | **Hybrid RAG** | Pipeline: Graph→Vector→Synthesis |
| Quality control | **Agentic RAG** | Add grading and refinement |
| Multiple domains | **Multi-Domain RAG** | Supervisor routing |

## 📁 File Structure

```
src/app/
├── graph.py                    # Main entry point
├── graphs/
│   ├── supervisor.py           # Main orchestrator
│   ├── domain_subgraphs.py     # Simple domains
│   └── *_subgraph.py          # Complex domains
├── tools/
│   └── *_tools.py             # Domain-specific tools
├── prompts/
│   └── *.md                   # Agent training materials
└── state.py                   # State definitions
```

## 🛠️ Common Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `neo4j_query_tool` | Structured data | `query_type="systems"` |
| `vector_search_tool` | Semantic patterns | `query="infrastructure config"` |
| `security_approval_gate` | Human oversight | For sensitive operations |
| `discover_incidents` | RCA analysis | Find related incidents |

## 🚦 Adding New Domain Checklist

- [ ] Create subgraph function in `domain_subgraphs.py`
- [ ] Add prompt file in `prompts/domain_name.md`
- [ ] Update supervisor routing in `supervisor.py`
- [ ] Add routing keywords to `route_query()`
- [ ] Add termination edge: `workflow.add_edge("domain", END)`
- [ ] Write tests for new domain
- [ ] Update documentation

## 🔧 Tool Development Template

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(param1: str, param2: int) -> str:
    """Tool description for agent"""
    try:
        # Tool implementation
        result = do_something(param1, param2)
        return f"Success: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
```

## 🧪 Testing Patterns

```python
# Unit test: Tool functionality
def test_tool():
    result = my_tool("input", 123)
    assert "expected" in result

# Integration test: Subgraph workflow
def test_subgraph():
    graph = create_domain_subgraph()
    response = graph.invoke(test_input)
    assert response["messages"][-1]["name"] == "domain_agent"

# E2E test: Full user journey
def test_user_journey():
    supervisor = create_supervisor()
    response = supervisor.invoke(user_query)
    assert "expected_content" in response["messages"][-1]["content"]
```

## 🎯 Performance Tips

### ✅ Fast Patterns
- Agents created at subgraph level
- Connection pooling for APIs
- Caching expensive operations
- Parallel tool execution (where possible)

### ❌ Slow Patterns
- Agents created in node functions
- New connections for each API call
- Repeated expensive calculations
- Sequential processing when parallel is possible

## 🔍 Debugging Checklist

**Agent not responding?**
- [ ] Check agent added to workflow correctly
- [ ] Verify tools are in list format `[tool1, tool2]`
- [ ] Confirm prompt is domain-specific

**Routing not working?**
- [ ] Check keyword matching in `route_query()`
- [ ] Verify domain added to conditional edges
- [ ] Ensure termination edge exists

**Performance issues?**
- [ ] Check agent creation pattern (subgraph vs node)
- [ ] Look for expensive operations in loops
- [ ] Verify connection management

## 💡 Pro Tips

1. **Start Simple**: Use Single Agent pattern first, enhance later
2. **Test Early**: Write tests as you develop, not after
3. **Follow Patterns**: Use existing domains as templates
4. **Error Gracefully**: All tools should handle failures
5. **Document Everything**: Update prompts and comments
6. **Performance First**: Always create agents at subgraph level

---

*For detailed explanations, see the full tutorial files 01-06 in this directory*
