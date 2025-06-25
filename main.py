#!/usr/bin/env python3
"""
Astra AI Assistant - Main Entry Point
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import asyncio
import logging
from pathlib import Path
from src.config import Config
from src.core.voice_assistant import VoiceAssistant
from src.server.api_server import APIServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for Astra AI Assistant."""
    try:
        # Load configuration
        config = Config()
        
        # Initialize voice assistant
        assistant = VoiceAssistant(config)
        
        # Initialize API server
        server = APIServer(assistant, config)
        
        # Start the server
        await server.start()
        
        # Keep the main task running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down Astra...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        # Cleanup
        if 'server' in locals():
            await server.stop()
        if 'assistant' in locals():
            await assistant.cleanup()

if __name__ == "__main__":
    # Create necessary directories
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Run the main async loop
    asyncio.run(main()) 