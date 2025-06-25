"""
Configuration management for Astra Voice Assistant
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class Config:
    """Configuration manager for Astra Voice Assistant"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.models_dir = Path(os.getenv("MODELS_DIR", "./models"))
        self.cache_dir = Path(os.getenv("CACHE_DIR", "./cache"))
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Server configuration
        self.server_host = os.getenv("SERVER_HOST", "0.0.0.0")
        self.server_port = int(os.getenv("SERVER_PORT", "8000"))
        self.debug_mode = os.getenv("DEBUG_MODE", "true").lower() == "true"
        
        # DeepSeek API configuration
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek/deepseek-r1-0528:free")
        
        # Weather API
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        
        # Search API
        self.bing_search_api_key = os.getenv("BING_SEARCH_API_KEY")
        
        # Security
        self.encryption_key = os.getenv("ENCRYPTION_KEY", "default_32_char_encryption_key_here")
        self.jwt_secret = os.getenv("JWT_SECRET", "default_jwt_secret_here")
        
        # Audio configuration
        self.sample_rate = int(os.getenv("SAMPLE_RATE", "16000"))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
        self.wake_word = os.getenv("WAKE_WORD", "astra")
        
        # TTS configuration
        self.tts_voice = os.getenv("TTS_VOICE", "en_GB-amy-medium")
        self.tts_speed = float(os.getenv("TTS_SPEED", "1.0"))
        self.tts_pitch = float(os.getenv("TTS_PITCH", "1.0"))
        
        # Feature toggles
        self.features = self._load_feature_toggles()
        
        # Personality configuration
        self.personality = {
            "name": "Astra",
            "voice": "sassy",
            "humor_level": 0.7,
            "sass_level": 0.6,
            "professional_mode": False,
            "greeting": "Hello! I'm Astra, your sassy AI assistant. How can I help you today?",
            "goodbye": "Goodbye! Don't forget I'm always here when you need me.",
            "thinking": "Let me think about that...",
            "confused": "I'm not quite sure what you mean. Could you rephrase that?",
            "error": "Oops! Something went wrong. Let me try again.",
            "jokes": [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the scarecrow win an award? Because he was outstanding in his field!",
                "Why don't eggs tell jokes? They'd crack each other up!",
                "What do you call a fake noodle? An impasta!",
                "Why did the math book look so sad? Because it had too many problems!"
            ]
        }
        
        # Initialize logging
        self._setup_logging()
    
    def _load_feature_toggles(self) -> Dict[str, bool]:
        """Load feature toggles from environment variables"""
        features = {}
        feature_list = [
            "WEATHER", "NEWS", "WEB_SEARCH", "CALENDAR", "EMAIL", "MUSIC",
            "NOTES", "TASKS", "CALCULATOR", "TRANSLATOR", "WIKIPEDIA",
            "SYSTEM_CONTROL", "MEDIA_PLAYER", "PODCASTS", "AUDIOBOOKS",
            "MEME_CREATOR", "VIDEO_PLAYER", "HABIT_TRACKER", "MOOD_TRACKER",
            "JOKE_GENERATOR", "QUOTE_GENERATOR", "VIRTUAL_PARTNER",
            "EDUCATION", "PROJECT_MANAGEMENT", "MEETING_SCHEDULER",
            "POMODORO", "STOPWATCH", "TIMER", "UNIT_CONVERTER",
            "DICTIONARY", "FILE_MANAGER", "APP_LAUNCHER", "AUTOMATION",
            "HARDWARE_CONTROL", "NETWORK_DIAGNOSTICS", "BATTERY_OPTIMIZATION",
            "SYSTEM_MONITORING", "NETWORK_DISCOVERY", "SYNC", "ENCRYPTION",
            "VOICEPRINT", "ACCESSIBILITY", "INTERNATIONALIZATION",
            "CRASH_REPORTING", "TELEMETRY"
        ]
        
        for feature in feature_list:
            env_var = f"ENABLE_{feature}"
            features[feature.lower()] = os.getenv(env_var, "true").lower() == "true"
        
        return features
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.debug_mode else logging.INFO
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(self.data_dir / "astra.log"),
                logging.StreamHandler()
            ]
        )
    
    def get_feature_status(self, feature_name: str) -> bool:
        """Get the status of a specific feature"""
        return self.features.get(feature_name.lower(), False)
    
    def update_feature_status(self, feature_name: str, enabled: bool):
        """Update the status of a specific feature"""
        self.features[feature_name.lower()] = enabled
    
    def save_config(self):
        """Save current configuration to file"""
        config_data = {
            "server": {
                "host": self.server_host,
                "port": self.server_port,
                "debug": self.debug_mode
            },
            "audio": {
                "sample_rate": self.sample_rate,
                "chunk_size": self.chunk_size,
                "wake_word": self.wake_word
            },
            "tts": {
                "voice": self.tts_voice,
                "speed": self.tts_speed,
                "pitch": self.tts_pitch
            },
            "features": self.features,
            "personality": self.personality
        }
        
        with open(self.data_dir / "config.json", "w") as f:
            json.dump(config_data, f, indent=2)
    
    def load_config(self):
        """Load configuration from file"""
        config_file = self.data_dir / "config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                config_data = json.load(f)
                
            # Update configuration from file
            if "server" in config_data:
                self.server_host = config_data["server"].get("host", self.server_host)
                self.server_port = config_data["server"].get("port", self.server_port)
                self.debug_mode = config_data["server"].get("debug", self.debug_mode)
            
            if "audio" in config_data:
                self.sample_rate = config_data["audio"].get("sample_rate", self.sample_rate)
                self.chunk_size = config_data["audio"].get("chunk_size", self.chunk_size)
                self.wake_word = config_data["audio"].get("wake_word", self.wake_word)
            
            if "tts" in config_data:
                self.tts_voice = config_data["tts"].get("voice", self.tts_voice)
                self.tts_speed = config_data["tts"].get("speed", self.tts_speed)
                self.tts_pitch = config_data["tts"].get("pitch", self.tts_pitch)
            
            if "features" in config_data:
                self.features.update(config_data["features"])
            
            if "personality" in config_data:
                self.personality.update(config_data["personality"])

# Global configuration instance
config = Config() 