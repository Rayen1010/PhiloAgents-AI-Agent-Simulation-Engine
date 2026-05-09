"""Main application entry point"""

import uvicorn
from chatbot.infrastructure.api import create_app
from chatbot.config import settings

# Create FastAPI app
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )
