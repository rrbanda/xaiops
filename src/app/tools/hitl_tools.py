from langchain_core.tools import tool
from langgraph.types import interrupt

@tool
def security_approval_gate(finding: str, risk_level: str) -> str:
    """Request human approval for security findings before proceeding."""
    approval = interrupt({
        "finding": finding,
        "risk_level": risk_level,
        "question": "Should we proceed with deeper security analysis?"
    })
    
    if approval.get("approved", False):
        return f"Approved: Proceeding with detailed analysis of {finding}"
    else:
        return f"Declined: Skipping detailed analysis of {finding}"
