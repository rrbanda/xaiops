#!/usr/bin/env python3
"""
LlamaStack A2A Agent using proper A2A SDK
"""
import asyncio
import json
import logging
import httpx
import uvicorn

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

class LlamaStackAgentExecutor(AgentExecutor):
    """LlamaStack Agent Executor for web search using correct endpoint"""
    
    def __init__(self):
        # LlamaStack configuration from working curl command
        self.base_url = "https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com/v1"
        self.agent_id = "b35d9295-552a-4b75-8fd9-8a4b9e1bef26"
        
    async def create_session(self, client: httpx.AsyncClient) -> str:
        """Create a new session for the LlamaStack agent"""
        session_url = f"{self.base_url}/agents/{self.agent_id}/session"
        
        session_payload = {
            "session_name": "xaiops_a2a_session"
        }
        
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = await client.post(session_url, headers=headers, json=session_payload)
        response.raise_for_status()
        
        session_data = response.json()
        session_id = session_data.get("session_id")
        
        if not session_id:
            raise Exception(f"Failed to get session_id from response: {session_data}")
            
        logger.info(f"Created LlamaStack session: {session_id}")
        return session_id

    async def call_llamastack(self, query: str) -> str:
        """Call LlamaStack endpoint with session creation and turn execution"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Step 1: Create session
                session_id = await self.create_session(client)
                
                # Step 2: Execute turn with streaming
                turn_url = f"{self.base_url}/agents/{self.agent_id}/session/{session_id}/turn"
                
                headers = {
                    "accept": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "stream": True,
                    "messages": [{"role": "user", "content": query}]
                }
                
                logger.info(f"Sending query to LlamaStack: {query}")
                
                async with client.stream("POST", turn_url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    
                    result_text = ""
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                
                                # Parse the SSE event structure from your working curl
                                if "event" in data and "payload" in data["event"]:
                                    payload_data = data["event"]["payload"]
                                    
                                    # Handle step progress with text deltas
                                    if (payload_data.get("event_type") == "step_progress" and 
                                        "delta" in payload_data and 
                                        payload_data["delta"].get("type") == "text"):
                                        
                                        text_content = payload_data["delta"].get("text", "")
                                        if text_content:
                                            result_text += text_content
                                    
                                    # Handle turn completion
                                    elif payload_data.get("event_type") == "turn_complete":
                                        turn_data = payload_data.get("turn", {})
                                        output_message = turn_data.get("output_message", {})
                                        if output_message.get("content"):
                                            # Use the complete response if available
                                            return output_message["content"]
                                            
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                logger.warning(f"Error parsing SSE data: {e}")
                                continue
                    
                    return result_text.strip() if result_text else "No web search results received"
                    
        except httpx.HTTPStatusError as e:
            return f"LlamaStack HTTP error {e.response.status_code}: {e.response.text}"
        except Exception as e:
            logger.error(f"LlamaStack error: {e}")
            return f"Web search error: {str(e)}"

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        logger.info(f"Processing web search query: {query}")
        
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
                    "Searching the web...",
                    task.contextId,
                    task.id,
                ),
            )
            
            search_result = await self.call_llamastack(query)
            
            await updater.add_artifact(
                [Part(root=TextPart(text=search_result))],
                name='web_search_result',
            )
            await updater.complete()

        except Exception as e:
            logger.error(f'Error processing web search: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())

def create_llamastack_agent_card(host: str = "localhost", port: int = 8002) -> AgentCard:
    """Create agent card for LlamaStack web search"""
    skills = [
        AgentSkill(
            id="web_search",
            name="Web Search",
            description="Real-time web search and current information",
            tags=["web", "search", "current", "news", "latest", "internet"]
        ),
        AgentSkill(
            id="current_events", 
            name="Current Events",
            description="Latest news and current events information",
            tags=["news", "current", "events", "recent", "today"]
        )
    ]
    
    return AgentCard(
        name="Web Search Agent",
        description="Real-time web search using LlamaStack",
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

def create_llamastack_server(host: str = "localhost", port: int = 8002):
    """Create LlamaStack A2A server"""
    agent_card = create_llamastack_agent_card(host, port)
    
    request_handler = DefaultRequestHandler(
        agent_executor=LlamaStackAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    server = A2AStarletteApplication(
        agent_card=agent_card, 
        http_handler=request_handler
    )
    
    return server.build()

if __name__ == "__main__":
    app = create_llamastack_server()
    uvicorn.run(app, host="localhost", port=8002)