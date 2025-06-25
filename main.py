#!/usr/bin/env python3
"""
Astra Voice Assistant - Main Entry Point
Enhanced version with feature management and personality
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.voice_assistant import voice_assistant
from src.core.feature_manager import get_feature_manager
from src.server.api_server import app
from src.config import config
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO if config.debug_mode else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/astra.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AstraAssistant:
    """Main Astra Voice Assistant application"""
    
    def __init__(self):
        self.voice_assistant = voice_assistant
        self.feature_manager = get_feature_manager()
        self.server_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.shutdown())
    
    async def initialize(self):
        """Initialize the voice assistant"""
        try:
            logger.info("Initializing Astra Voice Assistant...")
            
            # Create necessary directories
            Path("logs").mkdir(exist_ok=True)
            Path("data").mkdir(exist_ok=True)
            
            # Initialize voice assistant
            if not self.voice_assistant.is_initialized:
                await self.voice_assistant.initialize()
            
            # Enable default features
            await self._enable_default_features()
            
            logger.info("Astra Voice Assistant initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing Astra: {e}")
            raise
    
    async def _enable_default_features(self):
        """Enable default features"""
        default_features = ['weather', 'time', 'calculator', 'notes', 'reminder']
        
        for feature_name in default_features:
            if self.feature_manager.get_feature_info(feature_name):
                self.feature_manager.enable_feature(feature_name)
                logger.info(f"Enabled default feature: {feature_name}")
    
    async def start_server(self):
        """Start the API server"""
        try:
            logger.info(f"Starting API server on {config.server_host}:{config.server_port}")
            
            config = uvicorn.Config(
                app=app,
                host=config.server_host,
                port=config.server_port,
                log_level="info" if config.debug_mode else "warning",
                access_log=True
            )
            
            server = uvicorn.Server(config)
            self.server_task = asyncio.create_task(server.serve())
            
            logger.info("API server started successfully!")
            
        except Exception as e:
            logger.error(f"Error starting API server: {e}")
            raise
    
    async def start_voice_assistant(self):
        """Start the voice assistant"""
        try:
            logger.info("Starting voice assistant...")
            
            # Start voice assistant in background
            await self.voice_assistant.start()
            
            self.is_running = True
            logger.info("Voice assistant started successfully!")
            
        except Exception as e:
            logger.error(f"Error starting voice assistant: {e}")
            raise
    
    async def run(self):
        """Run the main application"""
        try:
            # Initialize
            await self.initialize()
            
            # Start server
            await self.start_server()
            
            # Start voice assistant
            await self.start_voice_assistant()
            
            # Keep running
            logger.info("Astra Voice Assistant is running!")
            logger.info("Press Ctrl+C to stop")
            
            # Wait for shutdown signal
            while self.is_running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error running Astra: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the application"""
        try:
            logger.info("Shutting down Astra Voice Assistant...")
            
            self.is_running = False
            
            # Stop voice assistant
            if self.voice_assistant.is_running:
                await self.voice_assistant.stop()
                logger.info("Voice assistant stopped")
            
            # Cancel server task
            if self.server_task and not self.server_task.done():
                self.server_task.cancel()
                try:
                    await self.server_task
                except asyncio.CancelledError:
                    pass
                logger.info("API server stopped")
            
            # Cleanup
            await self.voice_assistant.cleanup()
            
            logger.info("Astra Voice Assistant shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

def main():
    """Main entry point"""
    try:
        # Create and run Astra
        astra = AstraAssistant()
        
        # Run the event loop
        asyncio.run(astra.run())
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 