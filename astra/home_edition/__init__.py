"""
Astra Home Edition - Personal Voice Assistant

A free, feature-rich voice assistant for personal use with DRM protection.
"""

__version__ = "1.0.0"
__edition__ = "home"
__license__ = "Free for personal use"

import os
import sys
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import core components
from astra.core.config import settings
from astra.core.logging import get_logger
from astra.core.security import security_manager
from astra.core.database import database_manager

# Initialize Home Edition specific components
from .drm import HomeEditionDRM
from .features import HomeFeatures
from .server import HomeServer

# Set up logging
logger = get_logger("astra.home")

# Initialize DRM protection
drm_protection = HomeEditionDRM()

# Verify Home Edition license and features
if not drm_protection.verify_edition():
    logger.error("Home Edition verification failed")
    sys.exit(1)

# Export main components
__all__ = [
    "HomeEditionDRM",
    "HomeFeatures", 
    "HomeServer",
    "drm_protection",
] 