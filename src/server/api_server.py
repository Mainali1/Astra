"""
Enhanced API Server for Astra Voice Assistant
Provides REST and WebSocket endpoints for client communication
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..core.voice_assistant import voice_assistant
from ..core.feature_manager import get_feature_manager

logger = logging.getLogger(__name__)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"

class FeatureToggleRequest(BaseModel):
    feature_name: str
    enabled: bool

class FeatureInfo(BaseModel):
    name: str
    description: str
    category: str
    keywords: List[str]
    examples: List[str]
    enabled: bool
    version: str
    author: str

class SystemStatus(BaseModel):
    status: str
    uptime: str
    features_enabled: int
    features_total: int
    memory_usage: Dict[str, Any]
    last_activity: str

# Create FastAPI app
app = FastAPI(
    title="Astra Voice Assistant API",
    description="API for Astra Voice Assistant with feature management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            'client_id': client_id or f"client_{len(self.active_connections)}",
            'connected_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        logger.info(f"Client connected: {self.connection_data[websocket]['client_id']}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            client_id = self.connection_data[websocket]['client_id']
            self.active_connections.remove(websocket)
            del self.connection_data[websocket]
            logger.info(f"Client disconnected: {client_id}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
            self.connection_data[websocket]['last_activity'] = datetime.now().isoformat()
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")
            await self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
                self.connection_data[connection]['last_activity'] = datetime.now().isoformat()
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "Astra Voice Assistant API"
    }

# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    """Process chat message and return response"""
    try:
        # Process the message through voice assistant
        result = await voice_assistant.process_command(request.message)
        
        return {
            "success": result.get('success', False),
            "response": result.get('response', ''),
            "type": result.get('type', 'general'),
            "data": result.get('data'),
            "timestamp": datetime.now().isoformat(),
            "user_id": request.user_id
        }
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Feature management endpoints
@app.get("/features")
async def get_features(category: str = None):
    """Get all features or filter by category"""
    feature_manager = get_feature_manager()
    
    if category:
        features = feature_manager.list_features(category)
    else:
        features = feature_manager.list_features()
    
    return {
        "features": [FeatureInfo(**feature.__dict__) for feature in features],
        "total": len(features),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/features/categories")
async def get_feature_categories():
    """Get all feature categories"""
    feature_manager = get_feature_manager()
    return {
        "categories": feature_manager.categories,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/features/{feature_name}")
async def get_feature(feature_name: str):
    """Get specific feature information"""
    feature_manager = get_feature_manager()
    feature = feature_manager.get_feature_info(feature_name)
    
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    return FeatureInfo(**feature.__dict__)

@app.post("/features/{feature_name}/toggle")
async def toggle_feature(feature_name: str, request: FeatureToggleRequest):
    """Enable or disable a feature"""
    feature_manager = get_feature_manager()
    
    if request.enabled:
        success = feature_manager.enable_feature(feature_name)
    else:
        success = feature_manager.disable_feature(feature_name)
    
    if not success:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    return {
        "success": True,
        "feature": feature_name,
        "enabled": request.enabled,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/features/statistics")
async def get_feature_statistics():
    """Get feature statistics"""
    feature_manager = get_feature_manager()
    stats = feature_manager.get_feature_statistics()
    
    return {
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/features/suggestions")
async def get_feature_suggestions(query: str):
    """Get feature suggestions based on query"""
    feature_manager = get_feature_manager()
    suggestions = feature_manager.get_feature_suggestions(query)
    
    return {
        "suggestions": suggestions,
        "query": query,
        "timestamp": datetime.now().isoformat()
    }

# System endpoints
@app.get("/status")
async def get_system_status():
    """Get system status"""
    feature_manager = get_feature_manager()
    stats = feature_manager.get_feature_statistics()
    
    # Get memory usage (simplified)
    import psutil
    memory = psutil.virtual_memory()
    
    status = SystemStatus(
        status="running",
        uptime="0:00:00",  # TODO: Implement uptime tracking
        features_enabled=stats['enabled_features'],
        features_total=stats['total_features'],
        memory_usage={
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        },
        last_activity=datetime.now().isoformat()
    )
    
    return status

@app.get("/conversation/history")
async def get_conversation_history(limit: int = 10):
    """Get conversation history"""
    history = voice_assistant.get_conversation_history(limit)
    
    return {
        "history": history,
        "total": len(history),
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/conversation/history")
async def clear_conversation_history():
    """Clear conversation history"""
    voice_assistant.clear_conversation_history()
    
    return {
        "success": True,
        "message": "Conversation history cleared",
        "timestamp": datetime.now().isoformat()
    }

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Update last activity
            manager.connection_data[websocket]['last_activity'] = datetime.now().isoformat()
            
            # Process message
            if message_data.get('type') == 'chat':
                result = await voice_assistant.process_command(message_data['message'])
                
                # Send response back to client
                response = {
                    "type": "chat_response",
                    "success": result.get('success', False),
                    "response": result.get('response', ''),
                    "data": result.get('data'),
                    "timestamp": datetime.now().isoformat()
                }
                
                await manager.send_personal_message(response, websocket)
                
                # Broadcast status update to all clients
                await manager.broadcast({
                    "type": "status_update",
                    "status": "processing_complete",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_data.get('type') == 'ping':
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            
            elif message_data.get('type') == 'feature_toggle':
                feature_manager = get_feature_manager()
                feature_name = message_data.get('feature_name')
                enabled = message_data.get('enabled', False)
                
                if enabled:
                    success = feature_manager.enable_feature(feature_name)
                else:
                    success = feature_manager.disable_feature(feature_name)
                
                await manager.send_personal_message({
                    "type": "feature_toggle_response",
                    "success": success,
                    "feature_name": feature_name,
                    "enabled": enabled,
                    "timestamp": datetime.now().isoformat()
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Astra Voice Assistant API starting up...")
    
    # Initialize voice assistant if needed
    if not voice_assistant.is_initialized:
        await voice_assistant.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Astra Voice Assistant API shutting down...")
    
    # Cleanup voice assistant
    await voice_assistant.cleanup()
    
    # Close all WebSocket connections
    for connection in manager.active_connections.copy():
        manager.disconnect(connection)

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 