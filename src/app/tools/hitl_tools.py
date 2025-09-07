from langchain_core.tools import tool

@tool
def security_approval_gate(finding: str, risk_level: str) -> str:
    """Request human approval for security findings before proceeding."""
    # Simplified version - indicates approval needed without actual interruption
    return f"SECURITY REVIEW REQUIRED: {finding} (Risk Level: {risk_level}) - Manual approval needed"
