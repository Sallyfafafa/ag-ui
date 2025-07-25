"""
Development server for AutoGen integration testing
"""

import uvicorn
from .endpoint import create_autogen_app


def main():
    """Run the development server"""
    app = create_autogen_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )


if __name__ == "__main__":
    main()