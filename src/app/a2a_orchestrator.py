#!/usr/bin/env python3
"""
Smart Orchestrator using proper A2A SDK
"""
import asyncio
import logging
import uuid
from typing import Dict, TypedDict, List, Any, Optional

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

class RouterState(TypedDict, total=False):
    """State for the orchestrator workflow"""
    request: Optional[str]
    query: Optional[str] 
    messages: Optional[List[dict]]
    selected_agent: Optional[str]
    confidence: Optional[float]
    reasoning: Optional[str]
    response: Optional[str]
    success: Optional[bool]
    agent_url: Optional[str]
    agent_skills: Optional[List[str]]
    analysis_details: Optional[str]

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
        """Analyze request and select best agent using sophisticated skill matching"""
        logger.info(f"_analyze_request called with state: {state}")
        
        # Ensure agents are initialized
        await self.initialize_agents()
        
        # Extract request from multiple possible state formats
        request = None
        if "request" in state:
            request = state["request"]
            logger.info(f"Found request in state: {request}")
        elif "query" in state:
            request = state["query"]
            logger.info(f"Found query in state: {request}")
        elif "messages" in state and len(state["messages"]) > 0:
            # Extract from LangGraph messages format
            last_message = state["messages"][-1]
            if isinstance(last_message, dict):
                request = last_message.get("content", "")
            else:
                request = getattr(last_message, 'content', "")
            logger.info(f"Extracted from messages: {request}")
        else:
            # Fallback for unexpected state format
            request = str(state)
            logger.warning(f"Unexpected state format, using string representation: {state}")
        
        if not request:
            logger.error("No request content found in state")
            request = "empty request"
        
        # Sophisticated agent selection using registered agent skills
        best_agent = None
        best_score = 0.0
        
        request_lower = request.lower()
        logger.info(f"Analyzing request: '{request_lower}' against {len(self.agents)} agents")
        
        for agent_name, agent_card in self.agents.items():
            score = 0
            matched_skills = []
            
            for skill in agent_card.skills:
                skill_score = 0
                for tag in (skill.tags or []):
                    if tag.lower() in request_lower:
                        skill_score += 1
                        matched_skills.append(tag)
                        logger.info(f"Agent '{agent_name}' skill '{skill.name}' matched tag '{tag}'")
                
                score += skill_score
            
            if score > best_score:
                best_score = score
                best_agent = agent_name
                logger.info(f"New best agent: {agent_name} (score: {score}, skills: {matched_skills})")
        
        # Enhanced default routing logic with better keyword detection
        if not best_agent or best_score == 0:
            logger.info("No skill matches found, using enhanced keyword routing")
            
            if any(word in request_lower for word in ["server", "infrastructure", "database", "rca", "incident", "troubleshoot"]):
                best_agent = "Ops Infrastructure Agent"
                best_score = 0.7
                logger.info("Keyword routing to Ops Infrastructure Agent")
            elif any(word in request_lower for word in ["search", "news", "current", "latest", "kubernetes", "web", "internet"]):
                best_agent = "Web Search Agent"
                best_score = 0.8
                logger.info("Keyword routing to Web Search Agent")
            else:
                best_agent = "Ops Infrastructure Agent"  # Default fallback
                best_score = 0.5
                logger.info("Default fallback to Ops Infrastructure Agent")
        
        confidence = min(best_score / 3.0, 1.0) if best_score > 0 else 0.5
        reasoning = f"Selected {best_agent} based on skill matching (score: {best_score}) and keyword analysis"
        
        result_state = {
            "selected_agent": best_agent,
            "confidence": confidence,
            "reasoning": reasoning,
            "request": request,
            "analysis_details": f"Processed {len(self.agents)} agents, best score: {best_score}"
        }
        
        # Update state while preserving existing keys
        state.update(result_state)
        
        logger.info(f"_analyze_request completed: {result_state}")
        return state
    
    async def _route_to_agent(self, state):
        """Route request to selected agent with detailed information"""
        selected_agent = state["selected_agent"]
        request = state["request"]
        confidence = state.get("confidence", 0)
        reasoning = state.get("reasoning", "")
        
        logger.info(f"_route_to_agent: Routing '{request}' to '{selected_agent}'")
        
        agent_card = self.agents.get(selected_agent)
        if not agent_card:
            error_msg = f"Agent {selected_agent} not available"
            logger.error(error_msg)
            state["response"] = error_msg
            state["success"] = False
            return state
        
        # Provide detailed routing information
        agent_skills = [skill.name for skill in agent_card.skills]
        
        response = f"✅ Successfully routed to {selected_agent}\n"
        response += f"🎯 Confidence: {confidence:.2f}\n"
        response += f"🧠 Reasoning: {reasoning}\n"
        response += f"🔗 Agent URL: {agent_card.url}\n"
        response += f"🛠️ Available Skills: {', '.join(agent_skills)}\n"
        response += f"📝 Analysis: {state.get('analysis_details', 'No additional details')}"
        
        state["response"] = response
        state["success"] = True
        state["agent_url"] = agent_card.url
        state["agent_skills"] = agent_skills
        
        logger.info(f"_route_to_agent completed successfully for {selected_agent}")
        return state
    
    async def process_request(self, request: str) -> Dict:
        """Process request through proper LangGraph workflow"""
        # Ensure agents are initialized first
        await self.initialize_agents()
        
        logger.info(f"Processing request through LangGraph workflow: {request}")
        
        try:
            # Properly format initial state for RouterState TypedDict
            initial_state: RouterState = {
                "request": request,
                "query": request,
                "messages": [{"role": "user", "content": request}]
            }
            
            logger.info(f"Invoking workflow with state: {initial_state}")
            
            # Invoke the LangGraph workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            logger.info(f"Workflow completed with state: {final_state}")
            
            return {
                "success": True,
                "selected_agent": final_state.get("selected_agent"),
                "confidence": final_state.get("confidence", 0),
                "reasoning": final_state.get("reasoning", ""),
                "response": final_state.get("response", "No response")
            }
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            
            # Fallback to simple routing if workflow fails
            request_lower = request.lower()
            
            if any(word in request_lower for word in ["news", "latest", "current", "search", "kubernetes"]):
                selected_agent = "Web Search Agent"
                confidence = 0.6
                reasoning = f"Fallback routing to Web Search Agent due to workflow error: {e}"
            else:
                selected_agent = "Ops Infrastructure Agent"
                confidence = 0.4
                reasoning = f"Fallback routing to Ops Infrastructure Agent due to workflow error: {e}"
            
            return {
                "success": True,
                "selected_agent": selected_agent,
                "confidence": confidence,
                "reasoning": reasoning,
                "response": f"Workflow error fallback - routed to {selected_agent}"
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
        
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        
        try:
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    "Routing request to best agent...",
                    task.context_id,
                    task.id,
                ),
            )
            
            result = await self.orchestrator.process_request(query)
            
            if result.get("success", False) and result.get("selected_agent") == "Web Search Agent":
                # Actually call the Web Search Agent
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(
                        f"Forwarding to Web Search Agent for web search...",
                        task.context_id,
                        task.id,
                    ),
                )
                
                try:
                    # Call the Web Search Agent directly
                    agent_url = "http://localhost:8002"
                    payload = {
                        "jsonrpc": "2.0",
                        "id": str(uuid.uuid4()),
                        "method": "message/send",
                        "params": {
                            "message": {
                                "role": "user",
                                "messageId": str(uuid.uuid4()),
                                "contextId": str(uuid.uuid4()),
                                "parts": [{"type": "text", "text": query}]
                            },
                            "configuration": {"acceptedOutputModes": ["text"]}
                        }
                    }
                    
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(agent_url, json=payload)
                        response.raise_for_status()
                        agent_result = response.json()
                        
                        logger.info(f"Web Search Agent response: {agent_result}")
                        
                        # Extract the actual web search result
                        if "result" in agent_result and "artifacts" in agent_result["result"]:
                            artifacts = agent_result["result"]["artifacts"]
                            for artifact in artifacts:
                                parts = artifact.get("parts", [])
                                for part in parts:
                                    if part.get("kind") == "text":
                                        web_search_result = part.get("text", "No search results")
                                        break
                                else:
                                    continue
                                break
                            else:
                                web_search_result = "No search results found"
                        else:
                            web_search_result = f"Agent response: {str(agent_result)[:500]}..."
                        
                        response_text = f"🔍 Web Search Results:\n\n{web_search_result}"
                
                except Exception as e:
                    logger.error(f"Error calling Web Search Agent: {e}")
                    response_text = f"❌ Error contacting Web Search Agent: {str(e)}"
            else:
                # For other agents or errors, show routing information
                response_text = f"🎯 Agent Selection Results:\n"
                response_text += f"Selected Agent: {result.get('selected_agent')}\n"
                response_text += f"Confidence: {result.get('confidence'):.2f}\n"
                response_text += f"Reasoning: {result.get('reasoning')}\n"
                if not result.get("success", False):
                    response_text += f"Error: {result.get('error', 'Unknown error')}"
            
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