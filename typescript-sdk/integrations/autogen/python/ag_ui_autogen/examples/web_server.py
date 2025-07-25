"""
AutoGen Web Server Example

This example shows how to run AutoGen group chats through a web server using FastAPI.
The server provides REST endpoints for starting multi-agent group chats.
"""

import uvicorn
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the parent directory to the path so we can import ag_ui_autogen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ag_ui_autogen.endpoint import autogen_copilotkit_endpoint


def create_app() -> FastAPI:
    """Create the FastAPI application"""
    
    app = FastAPI(
        title="AutoGen Web Server Example",
        description="A web server demonstrating AutoGen integration with AG-UI",
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
    
    # Add AutoGen endpoints
    autogen_copilotkit_endpoint(app)
    
    @app.get("/")
    async def root():
        """Root endpoint with usage instructions"""
        return {
            "message": "AutoGen Web Server is running!",
            "endpoints": {
                "health": "/autogen/health",
                "groupchat": "/autogen/groupchat (POST)",
                "docs": "/docs"
            },
            "example_curl": """
curl -X POST "http://localhost:8001/autogen/groupchat" \\
     -H "Content-Type: application/json" \\
     -d '{
       "agents": [
         {"name": "user_proxy", "human_input_mode": "NEVER"},
         {"name": "assistant", "human_input_mode": "NEVER"},
         {"name": "critic", "human_input_mode": "NEVER"}
       ],
       "messages": [
         {"role": "user", "content": "How can I optimize my Python code for better performance?"}
       ]
     }'
            """
        }
    
    return app


if __name__ == "__main__":
    print("🚀 Starting AutoGen Web Server...")
    print("📖 Visit http://localhost:8001/docs for API documentation")
    print("🔗 Visit http://localhost:8001 for usage examples")
    print("")
    
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )