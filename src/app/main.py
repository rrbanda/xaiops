import sys
import os
sys.path.append(os.path.dirname(__file__))

from agents.supervisor import create_supervisor

# Export the compiled graph for LangGraph server
app = create_supervisor()
