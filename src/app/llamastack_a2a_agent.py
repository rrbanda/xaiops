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
    """LlamaStack Agent Executor for web search"""

    async def call_llamastack(self, query: str) -> str:
        """Call LlamaStack endpoint"""
        url = "https://lss-lss.apps.prod.rhoai.rh-aiservices-bu.com/v1/agents/fcf25b7f-4abf-4912-b29e-da317296a24b/session/693b3a94-a2e2-4984-ba7a-1ab341ccb409/turn"
        
        headers = {
            "accept": "text/event-stream",
            "Cache-Control": "no-cache", 
            "Content-Type": "application/json"
        }
        
        payload = {
            "stream": True,
            "messages": [{"role": "user", "content": query}]
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    result_text = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                if "choices" in data:
                                    for choice in data["choices"]:
                                        content = choice.get("delta", {}).get("content", "")
                                        if content:
                                            result_text += content
                            except:
                                continue
                    return result_text or "No web search results"
        except Exception as e:
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