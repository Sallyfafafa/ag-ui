"""
Development server for AG2 integration testing
"""

import uvicorn
from .endpoint import create_ag2_app


def main():
    """Run the development server"""
    app = create_ag2_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()