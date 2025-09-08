from langchain_core.tools import tool
from langgraph.types import interrupt

@tool
def security_approval_gate(finding: str, risk_level: str) -> str:
    """Request human approval for security findings before proceeding."""
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
