import sys
import os
import uuid
import json
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import httpx
from langgraph.graph import StateGraph, START, END, MessagesState

def extract_user_query(state):
    """Helper function to safely extract user query from state"""
    first_message = state["messages"][0]
    
    if isinstance(first_message, dict):
        content = first_message.get("content", "")
    else:
        content = getattr(first_message, 'content', "")
    
    if isinstance(content, list):
        content = " ".join(str(item) for item in content)
    elif not isinstance(content, str):
        content = str(content)
    
    return content

async def wait_for_task_completion(client, endpoint, task_id, max_wait=30):
    """Wait for A2A task to complete and return result"""
    for attempt in range(max_wait):
        await asyncio.sleep(1)
        
        get_payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/get",
            "params": {"id": task_id}
        }
        
        try:
            response = await client.post(endpoint, json=get_payload)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result and result["result"]:
                task_data = result["result"]
                task_state = task_data.get("status", {}).get("state")
                
                if task_state == "completed":
                    # Extract actual response text
                    artifacts = task_data.get("artifacts", [])
                    for artifact in artifacts:
                        parts = artifact.get("parts", [])
                        for part in parts:
                            if part.get("kind") == "text":
                                return part.get("text", "No response text")
                    return "Task completed but no response found"
                elif task_state == "failed":
                    error_msg = task_data.get("status", {}).get("message", "Task failed")
                    return f"External agent error: {error_msg}"
        except Exception as e:
            print(f"DEBUG: Error checking task status: {e}")
            continue
    
    return "External agent timeout - no response received"

def create_a2a_orchestrator_subgraph():
    """Subgraph that routes queries to A2A orchestrator and waits for actual responses"""
    
    async def a2a_orchestrator_node(state):
        """Node that forwards query to A2A orchestrator and returns actual response"""
        original_query = extract_user_query(state)
        
        print(f"DEBUG: A2A orchestrator processing: {original_query}")
        
        try:
            # Create A2A JSON-RPC request
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "message/send",
                "params": {
                    "message": {
                        "role": "user",
                        "messageId": str(uuid.uuid4()),
                        "contextId": str(uuid.uuid4()),
                        "parts": [{"type": "text", "text": original_query}]
                    },
                    "configuration": {"acceptedOutputModes": ["text"]}
                }
            }
            
            # Call A2A orchestrator and wait for actual response
            async with httpx.AsyncClient(timeout=60.0) as client:
                print(f"DEBUG: Sending request to A2A orchestrator...")
                response = await client.post(
                    "http://localhost:8000",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                print(f"DEBUG: A2A orchestrator response: {result}")
                
                # Handle A2A protocol response
                if "result" in result:
                    a2a_result = result["result"]
                    
                    # If it's a task, wait for completion
                    if isinstance(a2a_result, dict) and "id" in a2a_result:
                        task_id = a2a_result["id"]
                        print(f"DEBUG: Waiting for task {task_id} to complete...")
                        
                        actual_response = await wait_for_task_completion(
                            client, "http://localhost:8000", task_id
                        )
                        
                        return {
                            "messages": [{
                                "role": "assistant",
                                "content": f"External Agent Response:\n\n{actual_response}",
                                "name": "a2a_orchestrator"
                            }]
                        }
                    
                    # Handle direct response
                    elif isinstance(a2a_result, dict) and "parts" in a2a_result:
                        for part in a2a_result.get("parts", []):
                            if part.get("type") == "text":
                                response_text = part.get("text", "No response text")
                                return {
                                    "messages": [{
                                        "role": "assistant",
                                        "content": f"External Agent Response:\n\n{response_text}",
                                        "name": "a2a_orchestrator"
                                    }]
                                }
                
                # Fallback if no clear response structure
                return {
                    "messages": [{
                        "role": "assistant",
                        "content": f"A2A Orchestrator Response:\n\nReceived response but couldn't extract content. Raw result: {str(result)[:500]}...",
                        "name": "a2a_orchestrator"
                    }]
                }
                
        except httpx.HTTPError as e:
            error_msg = f"A2A orchestrator communication error: HTTP {e.response.status_code if hasattr(e, 'response') else 'unknown'}"
            print(f"DEBUG: {error_msg}")
            
            return {
                "messages": [{
                    "role": "assistant",
                    "content": f"External Agent Error:\n\n{error_msg}\n\nThe A2A orchestrator may be down or unreachable. Please ensure it's running on http://localhost:8000",
                    "name": "a2a_orchestrator"
                }]
            }
            
        except asyncio.TimeoutError:
            return {
                "messages": [{
                    "role": "assistant",
                    "content": f"External Agent Timeout:\n\nThe request timed out waiting for external agents to respond. This could indicate:\n- External agents are overloaded\n- Network connectivity issues\n- Complex query requiring more processing time",
                    "name": "a2a_orchestrator"
                }]
            }
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"DEBUG: A2A unexpected error: {error_msg}")
            
            return {
                "messages": [{
                    "role": "assistant",
                    "content": f"External Agent System Error:\n\n{error_msg}\n\nPlease check that all A2A agents are running:\n- A2A Orchestrator: http://localhost:8000\n- Web Search Agent: http://localhost:8002",
                    "name": "a2a_orchestrator"
                }]
            }
    
    # Build workflow
    workflow = StateGraph(MessagesState)
    workflow.add_node("a2a_orchestrator", a2a_orchestrator_node)
    workflow.add_edge(START, "a2a_orchestrator")
    workflow.add_edge("a2a_orchestrator", END)
    
    return workflow.compile()