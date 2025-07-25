"""
FastAPI endpoint for AutoGen integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio

from .sdk import AutoGenFlow, CopilotKitState


class AutoGenAgent(BaseModel):
    """Simple AutoGen Agent model for API"""
    name: str
    human_input_mode: str = "NEVER"
    max_consecutive_auto_reply: int = 10


class GroupChatRequest(BaseModel):
    """Request model for starting a group chat"""
    agents: List[AutoGenAgent]
    messages: List[Dict[str, Any]]
    state: Optional[Dict[str, Any]] = None


def autogen_copilotkit_endpoint(app: FastAPI):
    """
    Add AutoGen endpoints to FastAPI app
    """
    
    @app.post("/autogen/groupchat")
    async def start_autogen_groupchat(request: GroupChatRequest):
        """Start an AutoGen group chat"""
        try:
            # Create mock AutoGen agents (in real implementation, use actual AutoGen agents)
            agents = []
            for agent_data in request.agents:
                # Mock agent object
                agent = type('Agent', (), {
                    'name': agent_data.name,
                    'human_input_mode': agent_data.human_input_mode,
                    'max_consecutive_auto_reply': agent_data.max_consecutive_auto_reply
                })()
                agents.append(agent)
            
            # Create CopilotKit state
            state = CopilotKitState()
            state.messages = request.messages
            if request.state:
                state.state = request.state
            
            # Create and run AutoGen flow
            flow = AutoGenFlow(agents=agents, state=state)
            
            async def generate():
                try:
                    await flow.start_group_chat()
                except Exception as e:
                    error_response = {
                        "type": "error",
                        "error": str(e)
                    }
                    yield f"data: {json.dumps(error_response)}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/autogen/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "autogen-integration"}


def create_autogen_app() -> FastAPI:
    """Create a FastAPI app with AutoGen endpoints"""
    app = FastAPI(title="AutoGen AG-UI Integration", version="0.1.0")
    autogen_copilotkit_endpoint(app)
    return app