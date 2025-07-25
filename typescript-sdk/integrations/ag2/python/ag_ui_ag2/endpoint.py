"""
FastAPI endpoint for AG2 integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio

from .sdk import AG2Flow, CopilotKitState


class AG2Agent(BaseModel):
    """Simple AG2 Agent model for API"""
    name: str
    system_message: str


class ConversationRequest(BaseModel):
    """Request model for starting a conversation"""
    agents: List[AG2Agent]
    messages: List[Dict[str, Any]]
    state: Optional[Dict[str, Any]] = None


def ag2_copilotkit_endpoint(app: FastAPI):
    """
    Add AG2 endpoints to FastAPI app
    """
    
    @app.post("/ag2/conversation")
    async def start_ag2_conversation(request: ConversationRequest):
        """Start an AG2 multi-agent conversation"""
        try:
            # Create mock AG2 agents (in real implementation, use actual AG2 agents)
            agents = []
            for agent_data in request.agents:
                # Mock agent object
                agent = type('Agent', (), {
                    'name': agent_data.name,
                    'system_message': agent_data.system_message
                })()
                agents.append(agent)
            
            # Create CopilotKit state
            state = CopilotKitState()
            state.messages = request.messages
            if request.state:
                state.state = request.state
            
            # Create and run AG2 flow
            flow = AG2Flow(agents=agents, state=state)
            
            async def generate():
                try:
                    await flow.start_conversation()
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
    
    @app.get("/ag2/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "ag2-integration"}


def create_ag2_app() -> FastAPI:
    """Create a FastAPI app with AG2 endpoints"""
    app = FastAPI(title="AG2 AG-UI Integration", version="0.1.0")
    ag2_copilotkit_endpoint(app)
    return app