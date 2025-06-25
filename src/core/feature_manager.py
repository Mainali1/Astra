"""
Astra AI Assistant - Feature Manager Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import importlib
import logging
import pkgutil
from typing import Dict, Optional, Any
from src.config import Config

logger = logging.getLogger(__name__)

class FeatureManager:
    """Manages all available features and their lifecycle."""
    
    def __init__(self, config: Config):
        """Initialize the feature manager."""
        self.config = config
        self.features: Dict[str, Any] = {}
        self._load_features()
    
    def _load_features(self):
        """Dynamically load all available features."""
        try:
            # Import the features package
            import src.features as features_pkg
            
            # Iterate through all modules in the features package
            for _, name, _ in pkgutil.iter_modules(features_pkg.__path__):
                if self.config.is_feature_enabled(name):
                    try:
                        # Import the feature module
                        module = importlib.import_module(f"src.features.{name}")
                        
                        # Get the main feature class
                        feature_class = getattr(module, f"{name.title()}Feature")
                        
                        # Initialize the feature
                        feature = feature_class(self.config)
                        
                        # Store the feature instance
                        self.features[name] = feature
                        logger.info(f"Loaded feature: {name}")
                        
                    except Exception as e:
                        logger.error(f"Error loading feature {name}: {str(e)}")
                else:
                    logger.debug(f"Feature {name} is disabled")
                    
        except Exception as e:
            logger.error(f"Error loading features: {str(e)}")
    
    def get_feature(self, feature_name: str) -> Optional[Any]:
        """Get a feature by name."""
        return self.features.get(feature_name)
    
    def list_features(self) -> Dict[str, bool]:
        """List all features and their status."""
        return {
            name: bool(feature and feature.is_available())
            for name, feature in self.features.items()
        }
    
    async def cleanup(self):
        """Clean up all features."""
        for feature in self.features.values():
            try:
                if hasattr(feature, 'cleanup'):
                    await feature.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up feature: {str(e)}") 