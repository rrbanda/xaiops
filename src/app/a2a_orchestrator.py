#!/usr/bin/env python3
"""
Smart Orchestrator using proper A2A SDK
"""
import asyncio
import logging
import uuid
from typing import Dict

import httpx
import uvicorn
from langgraph.graph import StateGraph

from a2a.client import A2AClient, A2ACardResolver
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (
    AgentCard, AgentSkill, AgentCapabilities,
    InternalError, InvalidParamsError, Part, Task, TaskState, TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RouterState(dict):
    pass

class SmartOrchestrator:
    """Intelligent orchestrator using proper A2A SDK"""
    
    def __init__(self):
        self.agents: Dict[str, AgentCard] = {}
        self.workflow = self._create_workflow()
        self._initialized = False
    
    async def initialize_agents(self):
        """Initialize with default agent endpoints"""
        if self._initialized:
            return
            
        default_agents = [
            "http://localhost:8001",  # Ops agent
            "http://localhost:8002",  # LlamaStack agent
        ]
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for endpoint in default_agents:
                try:
                    resolver = A2ACardResolver(client, endpoint)
                    agent_card = await resolver.get_agent_card()
                    if agent_card:
                        self.agents[agent_card.name] = agent_card
                        logger.info(f"Registered {agent_card.name} from {endpoint}")
                except Exception as e:
                    logger.warning(f"Could not register {endpoint}: {e}")
        
        self._initialized = True
    
    def _create_workflow(self):
        """Create LangGraph workflow for routing"""
        workflow = StateGraph(RouterState)
        workflow.add_node("analyze", self._analyze_request)
        workflow.add_node("route", self._route_to_agent)
        workflow.add_edge("analyze", "route")
        workflow.set_entry_point("analyze")
        workflow.set_finish_point("route")
        return workflow.compile()
    
    async def _analyze_request(self, state):
        """Analyze request and select best agent"""
        # Ensure agents are initialized
        await self.initialize_agents()
        
        request = state["request"]
        best_agent = None
        best_score = 0.0
        
        request_lower = request.lower()
        
        for agent_name, agent_card in self.agents.items():
            score = 0
            for skill in agent_card.skills:
                for tag in (skill.tags or []):
                    if tag.lower() in request_lower:
                        score += 1
            
            if score > best_score:
                best_score = score
                best_agent = agent_name
        
        # Default routing logic
        if not best_agent:
            if any(word in request_lower for word in ["server", "infrastructure", "database", "rca"]):
                best_agent = "Ops Infrastructure Agent"
            elif any(word in request_lower for word in ["search", "news", "current", "latest"]):
                best_agent = "Web Search Agent"
            else:
                best_agent = "Ops Infrastructure Agent"  # Default fallback
        
        state.update({
            "selected_agent": best_agent,
            "confidence": min(best_score / 3.0, 1.0),
            "reasoning": f"Selected {best_agent} based on keyword matching (score: {best_score})"
        })
        return state
    
    async def _route_to_agent(self, state):
        """Route request to selected agent"""
        selected_agent = state["selected_agent"]
        request = state["request"]
        
        agent_card = self.agents.get(selected_agent)
        if not agent_card:
            state["response"] = f"Agent {selected_agent} not available"
            return state
        
        state["response"] = f"Successfully routed to {selected_agent} at {agent_card.url}"
        return state
    
    async def process_request(self, request: str) -> Dict:
        """Process request through workflow"""
        initial_state = {"request": request}
        final_state = await self.workflow.ainvoke(initial_state)
        
        return {
            "success": True,
            "selected_agent": final_state.get("selected_agent"),
            "confidence": final_state.get("confidence", 0),
            "reasoning": final_state.get("reasoning", ""),
            "response": final_state.get("response", "No response")
        }

class OrchestratorAgentExecutor(AgentExecutor):
    """Orchestrator Agent Executor"""

    def __init__(self):
        self.orchestrator = SmartOrchestrator()
        # Don't initialize agents here, do it lazily during execution

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        logger.info(f"Orchestrator processing: {query}")
        
        task = context.current_task
        if not task:
            if context.message:
                task = new_task(context.message)
                await event_queue.enqueue_event(task)
            else:
                raise ServerError(error=InvalidParamsError())
        
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        
        try:
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    "Routing request to best agent...",
                    task.contextId,
                    task.id,
                ),
            )
            
            result = await self.orchestrator.process_request(query)
            
            response_text = f"Agent Selection Results:\n"
            response_text += f"Selected Agent: {result.get('selected_agent')}\n"
            response_text += f"Confidence: {result.get('confidence'):.2f}\n"
            response_text += f"Reasoning: {result.get('reasoning')}\n"
            response_text += f"Result: {result.get('response')}"
            
            await updater.add_artifact(
                [Part(root=TextPart(text=response_text))],
                name='orchestrator_result',
            )
            await updater.complete()

        except Exception as e:
            logger.error(f'Orchestrator error: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())

def create_orchestrator_agent_card(host: str = "localhost", port: int = 8000) -> AgentCard:
    """Create orchestrator agent card"""
    skills = [
        AgentSkill(
            id="request_routing",
            name="Request Routing",
            description="Intelligent request routing to specialized agents",
            tags=["routing", "orchestration"]
        ),
        AgentSkill(
            id="agent_coordination",
            name="Agent Coordination",
            description="Multi-agent system coordination",
            tags=["coordination", "management"]
        )
    ]
    
    return AgentCard(
        name="Smart Orchestrator Agent",
        description="Intelligent agent routing using LangGraph and A2A protocol",
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

def create_orchestrator_server(host: str = "localhost", port: int = 8000):
    """Create orchestrator A2A server"""
    agent_card = create_orchestrator_agent_card(host, port)
    
    request_handler = DefaultRequestHandler(
        agent_executor=OrchestratorAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    server = A2AStarletteApplication(
        agent_card=agent_card, 
        http_handler=request_handler
    )
    
    return server.build()

if __name__ == "__main__":
    app = create_orchestrator_server()
    uvicorn.run(app, host="localhost", port=8000)