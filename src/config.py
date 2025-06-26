"""
Astra AI Assistant - Configuration Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import os
from pathlib import Path
from typing import Dict, Any, Set, List
from dotenv import load_dotenv
import json
import hashlib
from datetime import datetime


class Config:
    """Configuration management for Astra."""

    # Define edition-specific feature sets
    HOME_EDITION_FEATURES = {
        # Core Features
        "calculator",
        "timer",
        "reminder",
        "time",
        "notes",
        "weather",
        "dictionary",
        "translation",
        "wikipedia",
        # File & System
        "file_manager",
        "system_monitor",
        # Media & Entertainment
        "music",
        "jokes",
        # Productivity
        "calendar",
        "meeting_scheduler",
        "todo",
        "currency_converter",
        "crypto_prices",
        "web_search",
        # Basic Automation
        "automation_manager",
        "workflow_manager",
        "script_manager",
        "ocr",
    }

    ENTERPRISE_FEATURES = {
        # Include all home edition features
        *HOME_EDITION_FEATURES,
        # Enterprise-specific features
        "project_management",  # Advanced project tracking
        "team_collaboration",  # Team workspace features
        "role_management",  # Role-based access control
        "audit_logging",  # Detailed activity logging
        "advanced_security",  # Enhanced security features
        "compliance_tools",  # Compliance monitoring
        "team_analytics",  # Team performance analytics
        "resource_monitoring",  # Advanced resource tracking
        "license_management",  # License tracking
        "user_management",  # User administration
        "department_controls",  # Department-level settings
        "enterprise_backup",  # Advanced backup features
        "custom_workflows",  # Custom automation flows
        "api_access",  # API integration tools
        "advanced_automation",  # Advanced automation features
        "enterprise_integrations",  # Third-party integrations
    }

    def __init__(self):
        """Initialize configuration with defaults and environment variables."""
        # Load environment variables
        load_dotenv()

        # Core settings
        self.DEBUG = os.getenv("ASTRA_DEBUG", "false").lower() == "true"
        self.HOST = os.getenv("ASTRA_HOST", "0.0.0.0")
        self.PORT = int(os.getenv("ASTRA_PORT", "8000"))

        # Paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.MODELS_DIR = self.BASE_DIR / "models"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        self.LICENSE_FILE = self.BASE_DIR / "license.json"

        # Create necessary directories
        self.DATA_DIR.mkdir(exist_ok=True)
        self.MODELS_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)

        # Edition settings
        self.EDITION = os.getenv("ASTRA_EDITION", "home").lower()
        if self.EDITION not in ["home", "enterprise"]:
            self.EDITION = "home"

        # License management
        self.license_data = self._load_license()
        self.MAX_USERS = self._get_max_users()
        self.CURRENT_USERS = 0

        # AI settings
        self.OFFLINE_FIRST = os.getenv("ASTRA_OFFLINE_FIRST", "true").lower() == "true"
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

        # Speech settings
        self.WAKE_WORD = os.getenv("ASTRA_WAKE_WORD", "hey astra")
        self.TTS_VOICE = os.getenv("ASTRA_TTS_VOICE", "en_US")

        # Security settings
        self.ENCRYPTION_KEY = os.getenv("ASTRA_ENCRYPTION_KEY", "")
        self.JWT_SECRET = os.getenv("ASTRA_JWT_SECRET", "")
        self.ENABLE_SSL = os.getenv("ASTRA_ENABLE_SSL", "false").lower() == "true"

        # Feature toggles
        self.ENABLED_FEATURES = self._parse_features()

    def _load_license(self) -> Dict:
        """Load and validate license data."""
        try:
            if self.LICENSE_FILE.exists():
                with open(self.LICENSE_FILE, "r") as f:
                    license_data = json.load(f)

                # Validate license structure
                required_fields = ["key_hash", "max_users", "expiration"]
                if not all(field in license_data for field in required_fields):
                    print("Invalid license file structure")
                    return {}

                # Check expiration
                expiration = datetime.fromisoformat(license_data["expiration"])
                if datetime.now() > expiration:
                    print("License has expired")
                    return {}

                return license_data
            return {}
        except Exception as e:
            print(f"Error loading license: {e}")
            return {}

    def _get_max_users(self) -> int:
        """Get maximum allowed users based on edition and license."""
        if self.EDITION == "enterprise":
            return self.license_data.get("max_users", float("inf"))
        return 1 + self.license_data.get("additional_user_packs", 0)

    def _parse_features(self) -> Set[str]:
        """Parse enabled features based on edition and environment variables."""
        # Get manually enabled/disabled features from env
        feature_env = os.getenv("ASTRA_ENABLED_FEATURES", "")
        manual_features = set(f.strip() for f in feature_env.split(",") if f.strip())

        # Get base feature set for edition
        if self.EDITION == "enterprise":
            base_features = self.ENTERPRISE_FEATURES
        else:
            base_features = self.HOME_EDITION_FEATURES

        # Apply manual overrides
        if manual_features:
            # Enable specific features
            enabled = {f for f in manual_features if not f.startswith("-")}
            # Disable specific features
            disabled = {f[1:] for f in manual_features if f.startswith("-")}
            return (base_features | enabled) - disabled

        return base_features

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled for current edition."""
        # Check if feature exists in enabled features
        if feature_name not in self.ENABLED_FEATURES:
            return False

        # Check edition-specific restrictions
        if self.EDITION == "home" and feature_name not in self.HOME_EDITION_FEATURES:
            return False

        return True

    def can_add_user(self) -> bool:
        """Check if another user can be added."""
        return self.CURRENT_USERS < self.MAX_USERS

    def add_user(self) -> bool:
        """Add a user if possible."""
        if self.can_add_user():
            self.CURRENT_USERS += 1
            return True
        return False

    def remove_user(self) -> None:
        """Remove a user."""
        if self.CURRENT_USERS > 0:
            self.CURRENT_USERS -= 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "debug": self.DEBUG,
            "host": self.HOST,
            "port": self.PORT,
            "edition": self.EDITION,
            "offline_first": self.OFFLINE_FIRST,
            "wake_word": self.WAKE_WORD,
            "tts_voice": self.TTS_VOICE,
            "enabled_features": list(self.ENABLED_FEATURES),
            "max_users": self.MAX_USERS,
            "current_users": self.CURRENT_USERS,
        }

    def get_registered_users(self) -> List[str]:
        """Get list of registered users."""
        try:
            users_file = self.DATA_DIR / "users.json"
            if users_file.exists():
                with open(users_file, "r") as f:
                    users_data = json.load(f)
                return users_data.get("users", [])
            return []
        except Exception as e:
            print(f"Error loading users: {e}")
            return []

    def get_max_users(self) -> int:
        """Get maximum allowed users based on edition and license."""
        return self._get_max_users()

    def validate_license_key(self, key: str) -> bool:
        """Validate the provided license key."""
        if not key:
            return False

        try:
            # Get stored key hash from license data
            stored_key_hash = self.license_data.get("key_hash")
            if not stored_key_hash:
                return False

            # Hash the provided key
            key_hash = hashlib.sha256(key.encode()).hexdigest()

            # Compare hashes
            return key_hash == stored_key_hash

        except Exception as e:
            print(f"Error validating license key: {e}")
            return False

    def validate_enterprise_user_count(self) -> bool:
        """Validate enterprise edition user count against license."""
        if self.EDITION != "enterprise":
            return True

        try:
            # Get current user count
            current_users = len(self.get_registered_users())

            # Get maximum allowed users from license
            max_users = self.get_max_users()

            # Check if within limits
            return current_users <= max_users

        except Exception as e:
            print(f"Error validating enterprise user count: {e}")
            return False
