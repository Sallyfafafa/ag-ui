"""
AG2 Web Server Example

This example shows how to run AG2 agents through a web server using FastAPI.
The server provides REST endpoints for starting multi-agent conversations.
"""

import uvicorn
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the parent directory to the path so we can import ag_ui_ag2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ag_ui_ag2.endpoint import ag2_copilotkit_endpoint


def create_app() -> FastAPI:
    """Create the FastAPI application"""
    
    app = FastAPI(
        title="AG2 Web Server Example",
        description="A web server demonstrating AG2 integration with AG-UI",
        version="1.0.0"
    )
    
    # Add CORS middleware for web client access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify your frontend URLs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add AG2 endpoints
    ag2_copilotkit_endpoint(app)
    
    @app.get("/")
    async def root():
        """Root endpoint with usage instructions"""
        return {
            "message": "AG2 Web Server is running!",
            "endpoints": {
                "health": "/ag2/health",
                "conversation": "/ag2/conversation (POST)",
                "docs": "/docs"
            },
            "example_curl": """
curl -X POST "http://localhost:8000/ag2/conversation" \\
     -H "Content-Type: application/json" \\
     -d '{
       "agents": [
         {"name": "assistant", "system_message": "You are a helpful assistant"},
         {"name": "critic", "system_message": "You are a critical reviewer"}
       ],
       "messages": [
         {"role": "user", "content": "How can I improve my Python skills?"}
       ]
     }'
            """
        }
    
    return app


if __name__ == "__main__":
    print("🚀 Starting AG2 Web Server...")
    print("📖 Visit http://localhost:8000/docs for API documentation")
    print("🔗 Visit http://localhost:8000 for usage examples")
    print("")
    
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )