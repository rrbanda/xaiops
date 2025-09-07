from typing import TypedDict, List, Dict, Any, Literal, Optional, Annotated
from langgraph.graph.message import add_messages

class AppState(TypedDict, total=False):
    # Use Annotated + add_messages to append instead of overwrite
    messages: Annotated[List[Dict[str, Any]], add_messages]
    facts: Dict[str, Any]
    artifacts: Dict[str, Any]
    missing_fields: List[str]
    next: Literal["data_domain", "security_domain", "performance_domain", "compliance_domain", "learning_domain", "done"]
    is_complete: bool
    meta: Dict[str, Any]

def initial_state(user_input: Optional[str] = None) -> AppState:
    return {
        "messages": ([{"role": "user", "content": user_input}] if user_input else []),
        "facts": {},
        "artifacts": {},
        "missing_fields": [],
        "next": "data_domain",
        "is_complete": False,
        "meta": {"run_id": "temp", "step_count": 0}
    }
