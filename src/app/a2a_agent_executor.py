#!/usr/bin/env python3
"""
Ops Agent Executor using proper A2A SDK
"""
import logging
from typing import Optional

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

# Import your existing graph
from .graph import app as ops_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpsAgentExecutor(AgentExecutor):
    """Ops Agent Executor for infrastructure operations"""

    def __init__(self):
        logger.info("Initializing OpsAgentExecutor...")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())

        query = context.get_user_input()
        logger.info(f"Processing ops query: {query}")
        
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
                    "Processing infrastructure request...",
                    task.contextId,
                    task.id,
                ),
            )
            
            # Use your existing LangGraph system
            initial_state = {"messages": [{"role": "user", "content": query}]}
            result = ops_graph.invoke(initial_state)
            
            # Extract response from your graph result
            final_messages = result.get("messages", [])
            response_content = "Analysis completed"
            
            for msg in reversed(final_messages):
                if isinstance(msg, dict) and msg.get("role") == "assistant":
                    response_content = msg.get("content", response_content)
                    break
                elif hasattr(msg, 'content'):
                    response_content = msg.content
                    break
            
            # Complete the task with response
            await updater.add_artifact(
                [Part(root=TextPart(text=response_content))],
                name='ops_analysis_result',
            )
            await updater.complete()

        except Exception as e:
            logger.error(f'Error processing ops request: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> Optional[bool]:
        return None

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())