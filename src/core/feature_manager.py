"""
Astra AI Assistant - Feature Manager Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import importlib
import logging
import pkgutil
import asyncio
from typing import Dict, Optional, Any, List
from src.config import Config

logger = logging.getLogger(__name__)


class FeatureManager:
    """Manages all available features and their lifecycle."""

    def __init__(self, config: Config):
        """Initialize the feature manager."""
        self.config = config
        self.features: Dict[str, Any] = {}
        self.initialized_features: Dict[str, bool] = {}
        self.feature_dependencies: Dict[str, List[str]] = {}
        self._load_features()

    def _load_features(self):
        """Dynamically load all available features."""
        try:
            # Import the features package
            import src.features as features_pkg

            # First pass: Load all feature modules and check dependencies
            for _, name, _ in pkgutil.iter_modules(features_pkg.__path__):
                if self.config.is_feature_enabled(name):
                    try:
                        # Import the feature module
                        module = importlib.import_module(f"src.features.{name}")

                        # Get the main feature class
                        feature_class = getattr(module, f"{name.title()}Feature")

                        # Check for dependencies
                        if hasattr(feature_class, "DEPENDENCIES"):
                            self.feature_dependencies[name] = feature_class.DEPENDENCIES

                        # Initialize the feature
                        feature = feature_class(self.config)

                        # Store the feature instance
                        self.features[name] = feature
                        self.initialized_features[name] = False
                        logger.info(f"Loaded feature: {name}")

                    except Exception as e:
                        logger.error(f"Error loading feature {name}: {str(e)}")
                else:
                    logger.debug(f"Feature {name} is disabled")

            # Second pass: Initialize features in dependency order
            self._initialize_features()

        except Exception as e:
            logger.error(f"Error loading features: {str(e)}")

    def _initialize_features(self):
        """Initialize features in correct dependency order."""

        def has_unmet_dependencies(feature_name: str) -> bool:
            if feature_name not in self.feature_dependencies:
                return False
            for dep in self.feature_dependencies[feature_name]:
                if dep not in self.features or not self.initialized_features.get(dep, False):
                    return True
            return False

        # Initialize features without dependencies first
        for name, feature in self.features.items():
            if not has_unmet_dependencies(name):
                try:
                    if hasattr(feature, "initialize"):
                        asyncio.create_task(feature.initialize())
                    self.initialized_features[name] = True
                    logger.info(f"Initialized feature: {name}")
                except Exception as e:
                    logger.error(f"Error initializing feature {name}: {str(e)}")

        # Initialize remaining features in dependency order
        while True:
            initialized_count = sum(self.initialized_features.values())

            for name, feature in self.features.items():
                if not self.initialized_features[name] and not has_unmet_dependencies(name):
                    try:
                        if hasattr(feature, "initialize"):
                            asyncio.create_task(feature.initialize())
                        self.initialized_features[name] = True
                        logger.info(f"Initialized feature: {name}")
                    except Exception as e:
                        logger.error(f"Error initializing feature {name}: {str(e)}")

            # If no new features were initialized, break
            if initialized_count == sum(self.initialized_features.values()):
                break

    def get_feature(self, feature_name: str) -> Optional[Any]:
        """Get a feature by name."""
        feature = self.features.get(feature_name)
        if feature and not self.initialized_features.get(feature_name, False):
            logger.warning(f"Feature {feature_name} is not fully initialized")
        return feature

    def list_features(self) -> Dict[str, Dict[str, Any]]:
        """List all features and their status."""
        return {
            name: {
                "available": bool(feature and feature.is_available()),
                "initialized": self.initialized_features.get(name, False),
                "edition": (
                    "enterprise"
                    if name in self.config.ENTERPRISE_FEATURES - self.config.HOME_EDITION_FEATURES
                    else "home"
                ),
            }
            for name, feature in self.features.items()
        }

    async def cleanup(self):
        """Clean up all features in reverse dependency order."""
        # Get features in reverse dependency order
        cleanup_order = []
        visited = set()

        def visit(feature_name: str):
            if feature_name in visited:
                return
            visited.add(feature_name)
            # Visit dependencies first
            for dep in self.feature_dependencies.get(feature_name, []):
                visit(dep)
            cleanup_order.append(feature_name)

        for name in self.features:
            visit(name)

        # Cleanup features in reverse order
        for name in reversed(cleanup_order):
            feature = self.features.get(name)
            if feature:
                try:
                    if hasattr(feature, "cleanup"):
                        await feature.cleanup()
                    logger.info(f"Cleaned up feature: {name}")
                except Exception as e:
                    logger.error(f"Error cleaning up feature {name}: {str(e)}")

    def is_feature_available(self, feature_name: str) -> bool:
        """Check if a feature is available and initialized."""
        if not self.config.is_feature_enabled(feature_name):
            return False
        feature = self.features.get(feature_name)
        if not feature:
            return False
        return self.initialized_features.get(feature_name, False) and feature.is_available()
