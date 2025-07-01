"""
Astra AI-Driven Productivity & Project Management Assistant

A sophisticated voice assistant available in Home and Enterprise editions.
"""

__version__ = "1.0.0"
__author__ = "Astra Technologies"
__license__ = "Commercial"

import os
import sys
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set up environment
os.environ.setdefault("ASTRA_ENV", "development")

# Import core components
from .core.config import settings
from .core.logging import setup_logging

# Initialize logging
setup_logging()

# Export main components
__all__ = [
    "settings",
    "setup_logging",
] 