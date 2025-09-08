#!/usr/bin/env python3
"""
Ops A2A Server using proper A2A SDK
"""
import logging
import uvicorn
import httpx
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities

from .a2a_agent_executor import OpsAgentExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_ops_agent_card(host: str = "localhost", port: int = 8001) -> AgentCard:
    """Create agent card for ops system"""
    skills = [
        AgentSkill(
            id="infrastructure_analysis",
            name="Infrastructure Analysis", 
            description="Neo4j infrastructure queries and system analysis",
            tags=["infrastructure", "servers", "systems", "neo4j", "database"]
        ),
        AgentSkill(
            id="security_analysis",
            name="Security Analysis",
            description="Security vulnerability assessment",
            tags=["security", "vulnerabilities", "compliance"]
        ),
        AgentSkill(
            id="rca_investigation", 
            name="Root Cause Analysis",
            description="Incident investigation and troubleshooting",
            tags=["rca", "incidents", "troubleshooting", "analysis"]
        ),
        AgentSkill(
            id="performance_monitoring",
            name="Performance Monitoring", 
            description="System performance analysis and monitoring",
            tags=["performance", "monitoring", "metrics"]
        )
    ]
    
    return AgentCard(
        name="Ops Infrastructure Agent",
        description="Enterprise infrastructure management and incident response using LangGraph",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=True,
            stateTransitionHistory=False
        ),
        skills=skills,
        defaultInputModes=["text"],
        defaultOutputModes=["text"]
    )

def create_ops_server(host: str = "localhost", port: int = 8001):
    """Create ops A2A server"""
    agent_card = create_ops_agent_card(host, port)
    
    # Create A2A server components - simplified to match actual API
    request_handler = DefaultRequestHandler(
        agent_executor=OpsAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    server = A2AStarletteApplication(
        agent_card=agent_card, 
        http_handler=request_handler
    )
    
    return server.build()

if __name__ == "__main__":
    app = create_ops_server()
    uvicorn.run(app, host="localhost", port=8001)