"""
Astra AI Assistant - API Server Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.config import Config
from src.core.voice_assistant import VoiceAssistant

logger = logging.getLogger(__name__)


class TextInput(BaseModel):
    """Text input model."""

    text: str
    context: Optional[Dict[str, Any]] = None


class APIServer:
    """FastAPI server for Astra."""

    def __init__(self, assistant: VoiceAssistant, config: Config):
        """Initialize the API server."""
        self.assistant = assistant
        self.config = config
        self.app = FastAPI(title="Astra AI Assistant API", description="API for Astra AI Assistant", version="1.0.0")

        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        """Set up CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # TODO: Configure properly for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Set up API routes."""

        @self.app.post("/api/text")
        async def process_text(input_data: TextInput):
            """Process text input."""
            try:
                response = await self.assistant.process_input(input_data.text)
                return {"response": response}
            except Exception as e:
                logger.error(f"Error processing text: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/features")
        async def list_features():
            """List available features."""
            try:
                features = self.assistant.feature_manager.list_features()
                return {"features": features}
            except Exception as e:
                logger.error(f"Error listing features: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time communication."""
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_json()
                    if "text" in data:
                        response = await self.assistant.process_input(data["text"])
                        await websocket.send_json({"response": response})
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
            finally:
                await websocket.close()

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy"}

    async def start(self):
        """Start the API server."""
        import uvicorn

        config = uvicorn.Config(self.app, host=self.config.HOST, port=self.config.PORT, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    async def stop(self):
        """Stop the API server."""
        # Uvicorn handles shutdown automatically
