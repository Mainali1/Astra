"""
Astra AI Assistant - Configuration Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class Config:
    """Configuration management for Astra."""
    
    def __init__(self):
        """Initialize configuration with defaults and environment variables."""
        # Load environment variables
        load_dotenv()
        
        # Core settings
        self.DEBUG = os.getenv('ASTRA_DEBUG', 'false').lower() == 'true'
        self.HOST = os.getenv('ASTRA_HOST', '0.0.0.0')
        self.PORT = int(os.getenv('ASTRA_PORT', '8000'))
        
        # Paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.MODELS_DIR = self.BASE_DIR / 'models'
        self.LOGS_DIR = self.BASE_DIR / 'logs'
        
        # Create necessary directories
        self.DATA_DIR.mkdir(exist_ok=True)
        self.MODELS_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
        
        # Edition settings
        self.EDITION = os.getenv('ASTRA_EDITION', 'single').lower()
        self.MAX_USERS = 5 if self.EDITION == 'single' else None
        
        # AI settings
        self.OFFLINE_FIRST = os.getenv('ASTRA_OFFLINE_FIRST', 'true').lower() == 'true'
        self.DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
        
        # Speech settings
        self.WAKE_WORD = os.getenv('ASTRA_WAKE_WORD', 'hey astra')
        self.TTS_VOICE = os.getenv('ASTRA_TTS_VOICE', 'en_US')
        
        # Security settings
        self.ENCRYPTION_KEY = os.getenv('ASTRA_ENCRYPTION_KEY', '')
        self.JWT_SECRET = os.getenv('ASTRA_JWT_SECRET', '')
        self.ENABLE_SSL = os.getenv('ASTRA_ENABLE_SSL', 'false').lower() == 'true'
        
        # Feature toggles
        self.ENABLED_FEATURES = self._parse_features()
    
    def _parse_features(self) -> Dict[str, bool]:
        """Parse enabled features from environment variables."""
        features = {}
        feature_env = os.getenv('ASTRA_ENABLED_FEATURES', '*')
        
        if feature_env == '*':
            # All features enabled
            return {'*': True}
        
        for feature in feature_env.split(','):
            feature = feature.strip()
            if feature:
                features[feature] = True
        
        return features
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'debug': self.DEBUG,
            'host': self.HOST,
            'port': self.PORT,
            'edition': self.EDITION,
            'offline_first': self.OFFLINE_FIRST,
            'wake_word': self.WAKE_WORD,
            'tts_voice': self.TTS_VOICE,
            'enabled_features': self.ENABLED_FEATURES
        }
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        if '*' in self.ENABLED_FEATURES:
            return True
        return feature_name in self.ENABLED_FEATURES 