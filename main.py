#!/usr/bin/env python3
"""
Astra AI Assistant - Main Entry Point
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Set
from src.config import Config
from src.core.voice_assistant import VoiceAssistant
from src.server.api_server import APIServer
from installer_config import AstraEdition, InstallerConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/astra.log')
    ]
)
logger = logging.getLogger(__name__)

class AstraApp:
    """Main application class for Astra AI Assistant."""
    
    def __init__(self):
        """Initialize the Astra application."""
        self.config: Optional[Config] = None
        self.assistant: Optional[VoiceAssistant] = None
        self.server: Optional[APIServer] = None
        self.edition: Optional[AstraEdition] = None
        
    def determine_edition(self) -> AstraEdition:
        """Determine which edition is installed based on available features."""
        try:
            # Check for enterprise-specific files
            enterprise_indicators = [
                Path("src/features/email_manager.py"),
                Path("src/features/meeting_scheduler.py"),
                Path("src/server/enterprise")
            ]
            
            is_enterprise = all(path.exists() for path in enterprise_indicators)
            return AstraEdition.ENTERPRISE if is_enterprise else AstraEdition.HOME
            
        except Exception as e:
            logger.warning(f"Error determining edition: {e}. Defaulting to Home Edition.")
            return AstraEdition.HOME
        
    async def validate_license(self) -> bool:
        """Validate the license based on edition."""
        if not self.config or not self.edition:
            return False
            
        if self.edition == AstraEdition.HOME:
            # For Home Edition, check user count
            user_count = len(self.config.get_registered_users())
            max_users = self.config.get_max_users()
            if user_count > max_users:
                logger.error(f"User limit exceeded. Current: {user_count}, Maximum: {max_users}")
                return False
            return True
            
        # Enterprise Edition license validation
        try:
            license_file = Path(self.config.LICENSE_FILE)
            if not license_file.exists():
                logger.error("Enterprise Edition requires a valid license file")
                return False
                
            with open(license_file, 'r') as f:
                license_data = json.load(f)
                
            # Validate license key
            if not self.config.validate_license_key(license_data.get('key', '')):
                logger.error("Invalid license key")
                return False
                
            # Check expiration
            if 'expiration' in license_data:
                expiration = datetime.fromisoformat(license_data['expiration'])
                if datetime.now() > expiration:
                    logger.error("License has expired")
                    return False
                    
            # Validate user count for enterprise
            if not self.config.validate_enterprise_user_count():
                logger.error("Enterprise license user limit exceeded")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating license: {str(e)}")
            return False
            
    def validate_features(self) -> bool:
        """Validate that only edition-specific features are present."""
        if not self.edition:
            return False
            
        allowed_features = InstallerConfig.get_features(self.edition)
        enabled_features = set(self.config.ENABLED_FEATURES if self.config else set())
        
        # Check for unauthorized features
        unauthorized = enabled_features - allowed_features
        if unauthorized:
            logger.error(f"Unauthorized features detected for {self.edition.value} edition: {unauthorized}")
            return False
            
        return True
            
    async def setup(self) -> bool:
        """Set up the application."""
        try:
            # Determine edition
            self.edition = self.determine_edition()
            logger.info(f"Detected Astra {self.edition.value.title()} Edition")
            
            # Load configuration
            self.config = Config()
            
            # Validate features
            if not self.validate_features():
                return False
                
            # Validate license
            if not await self.validate_license():
                return False
                
            # Initialize voice assistant with edition-specific features
            self.assistant = VoiceAssistant(self.config)
            
            # Initialize API server
            self.server = APIServer(self.assistant, self.config)
            
            return True
            
        except Exception as e:
            logger.error(f"Error during setup: {str(e)}")
            return False
            
    async def run(self):
        """Run the application."""
        try:
            # Set up the application
            if not await self.setup():
                return
                
            if not self.server or not self.config or not self.edition:
                logger.error("Application not properly initialized")
                return
                
            # Start the server
            await self.server.start()
            
            # Log startup information
            logger.info(f"Started Astra AI Assistant - {self.edition.value.title()} Edition")
            logger.info(f"Available features: {list(self.config.ENABLED_FEATURES)}")
            
            # Keep the main task running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down Astra...")
        except Exception as e:
            logger.error(f"Fatal error: {str(e)}", exc_info=True)
        finally:
            await self.cleanup()
            
    async def cleanup(self):
        """Clean up resources."""
        if self.server:
            await self.server.stop()
        if self.assistant:
            await self.assistant.cleanup()

async def main():
    """Main entry point for Astra AI Assistant."""
    app = AstraApp()
    await app.run()

if __name__ == "__main__":
    # Create necessary directories
    for dir_name in ['data', 'logs', 'models']:
        Path(dir_name).mkdir(exist_ok=True)
    
    # Run the main async loop
    asyncio.run(main()) 