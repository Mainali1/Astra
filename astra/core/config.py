"""
Configuration management for Astra voice assistant.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
from pydantic_settings import BaseSettings as PydanticBaseSettings


class Settings(PydanticBaseSettings):
    """Main configuration settings for Astra."""
    
    # Application Settings
    app_name: str = "Astra"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="ASTRA_DEBUG")
    environment: str = Field(default="development", env="ASTRA_ENV")
    
    # Edition Settings
    edition: str = Field(default="home", env="ASTRA_EDITION")  # "home" or "enterprise"
    license_key: Optional[str] = Field(default=None, env="ASTRA_LICENSE_KEY")
    
    # Server Settings
    host: str = Field(default="127.0.0.1", env="ASTRA_HOST")
    port: int = Field(default=8000, env="ASTRA_PORT")
    workers: int = Field(default=1, env="ASTRA_WORKERS")
    
    # Database Settings
    database_url: str = Field(default="sqlite:///astra.db", env="ASTRA_DATABASE_URL")
    database_encryption_key: Optional[str] = Field(default=None, env="ASTRA_DB_ENCRYPTION_KEY")
    
    # AI Model Settings
    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    default_model: str = Field(default="deepseek-chat", env="ASTRA_DEFAULT_MODEL")
    
    # Audio Settings
    sample_rate: int = Field(default=16000, env="ASTRA_SAMPLE_RATE")
    chunk_size: int = Field(default=1024, env="ASTRA_CHUNK_SIZE")
    wake_word: str = Field(default="hey astra", env="ASTRA_WAKE_WORD")
    
    # Security Settings
    secret_key: str = Field(default="your-secret-key-here", env="ASTRA_SECRET_KEY")
    encryption_key: Optional[str] = Field(default=None, env="ASTRA_ENCRYPTION_KEY")
    jwt_secret: str = Field(default="your-jwt-secret-here", env="ASTRA_JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="ASTRA_JWT_ALGORITHM")
    jwt_expiration: int = Field(default=3600, env="ASTRA_JWT_EXPIRATION")
    
    # File Storage Settings
    data_dir: Path = Field(default=Path("./data"), env="ASTRA_DATA_DIR")
    models_dir: Path = Field(default=Path("./models"), env="ASTRA_MODELS_DIR")
    logs_dir: Path = Field(default=Path("./logs"), env="ASTRA_LOGS_DIR")
    
    # Cache Settings
    cache_enabled: bool = Field(default=True, env="ASTRA_CACHE_ENABLED")
    cache_ttl: int = Field(default=3600, env="ASTRA_CACHE_TTL")
    redis_url: Optional[str] = Field(default=None, env="ASTRA_REDIS_URL")
    
    # API Settings
    cors_origins: list = Field(default=["http://localhost:3000"], env="ASTRA_CORS_ORIGINS")
    rate_limit_enabled: bool = Field(default=True, env="ASTRA_RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="ASTRA_RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="ASTRA_RATE_LIMIT_WINDOW")
    
    # Logging Settings
    log_level: str = Field(default="INFO", env="ASTRA_LOG_LEVEL")
    log_format: str = Field(default="json", env="ASTRA_LOG_FORMAT")
    
    # Home Edition Settings
    max_users_home: int = Field(default=5, env="ASTRA_MAX_USERS_HOME")
    expansion_pack_price: float = Field(default=10.0, env="ASTRA_EXPANSION_PACK_PRICE")
    expansion_pack_size: int = Field(default=5, env="ASTRA_EXPANSION_PACK_SIZE")
    
    # Enterprise Edition Settings
    enterprise_features_enabled: bool = Field(default=False, env="ASTRA_ENTERPRISE_FEATURES")
    ldap_enabled: bool = Field(default=False, env="ASTRA_LDAP_ENABLED")
    ldap_server: Optional[str] = Field(default=None, env="ASTRA_LDAP_SERVER")
    ldap_bind_dn: Optional[str] = Field(default=None, env="ASTRA_LDAP_BIND_DN")
    ldap_bind_password: Optional[str] = Field(default=None, env="ASTRA_LDAP_BIND_PASSWORD")
    
    # External API Keys
    openweather_api_key: Optional[str] = Field(default=None, env="OPENWEATHER_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    stripe_secret_key: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    stripe_publishable_key: Optional[str] = Field(default=None, env="STRIPE_PUBLISHABLE_KEY")
    
    # Performance Settings
    max_concurrent_requests: int = Field(default=100, env="ASTRA_MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="ASTRA_REQUEST_TIMEOUT")
    memory_limit_mb: int = Field(default=512, env="ASTRA_MEMORY_LIMIT_MB")
    
    # Plugin Settings
    plugins_enabled: bool = Field(default=True, env="ASTRA_PLUGINS_ENABLED")
    plugin_dir: Path = Field(default=Path("./plugins"), env="ASTRA_PLUGIN_DIR")
    plugin_sandbox_enabled: bool = Field(default=True, env="ASTRA_PLUGIN_SANDBOX")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        for directory in [self.data_dir, self.models_dir, self.logs_dir, self.plugin_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def is_enterprise(self) -> bool:
        """Check if running in enterprise mode."""
        return self.edition.lower() == "enterprise"
    
    @property
    def is_home(self) -> bool:
        """Check if running in home mode."""
        return self.edition.lower() == "home"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        """Get feature-specific configuration."""
        feature_configs = {
            "voice_recognition": {
                "enabled": True,
                "offline_model": "vosk",
                "online_model": "deepseek",
                "confidence_threshold": 0.8,
            },
            "text_to_speech": {
                "enabled": True,
                "offline_model": "piper",
                "online_model": "deepseek",
                "voice_options": ["en-US", "en-GB", "es-ES", "fr-FR"],
            },
            "natural_language": {
                "enabled": True,
                "model": self.default_model,
                "context_window": 4096,
                "max_tokens": 2048,
            },
            "security": {
                "encryption_enabled": True,
                "hardware_fingerprinting": True,
                "license_validation": True,
                "audit_logging": self.is_enterprise,
            },
        }
        return feature_configs.get(feature_name, {})


# Global settings instance
settings = Settings() 