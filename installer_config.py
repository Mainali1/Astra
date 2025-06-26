"""
Configuration for Astra's Home and Enterprise edition installers.
This file defines which features, dependencies, and files should be included in each edition.
"""

from enum import Enum
from typing import List, Dict, Set

class AstraEdition(Enum):
    HOME = "home"
    ENTERPRISE = "enterprise"

class InstallerConfig:
    # Core features available in both editions
    CORE_FEATURES = {
        "calculator",
        "time",
        "timer",
        "weather",
        "system_monitor",
        "dictionary",
        "web_search",
        "wikipedia",
    }

    # Features exclusive to Home Edition
    HOME_FEATURES = CORE_FEATURES | {
        "notes",
        "reminder",
        "music",
        "translation",
        "crypto_prices",
        "currency_converter",
    }

    # Features exclusive to Enterprise Edition
    ENTERPRISE_FEATURES = CORE_FEATURES | {
        "email_manager",
        "meeting_scheduler",
        "calendar",
        "file_manager",
        "notes",  # Enhanced version with multi-user support
        "reminder",  # Enhanced version with team features
    }

    # Dependencies required for each edition
    DEPENDENCIES = {
        AstraEdition.HOME: [
            "deepseek-ai",
            "vosk",
            "piper-tts",
            "fastapi",
            "sqlcipher",
            "pydantic",
            "python-dotenv",
            "aiohttp",
        ],
        AstraEdition.ENTERPRISE: [
            "deepseek-ai",
            "vosk",
            "piper-tts",
            "fastapi",
            "sqlcipher",
            "pydantic",
            "python-dotenv",
            "aiohttp",
            "ldap3",  # For enterprise authentication
            "psycopg2",  # For PostgreSQL support
            "redis",  # For caching and session management
            "cryptography",  # For enhanced security
        ]
    }

    # Files to exclude from each edition
    EXCLUDE_PATTERNS = {
        AstraEdition.HOME: [
            "src/features/email_manager.py",
            "src/features/meeting_scheduler.py",
            "src/features/calendar.py",
            "src/features/file_manager.py",
            "src/server/enterprise/*",
            "src/core/enterprise/*",
        ],
        AstraEdition.ENTERPRISE: []  # Enterprise includes all files
    }

    @staticmethod
    def get_features(edition: AstraEdition) -> Set[str]:
        """Get the set of features for a specific edition."""
        if edition == AstraEdition.HOME:
            return InstallerConfig.HOME_FEATURES
        return InstallerConfig.ENTERPRISE_FEATURES

    @staticmethod
    def get_dependencies(edition: AstraEdition) -> List[str]:
        """Get the list of dependencies for a specific edition."""
        return InstallerConfig.DEPENDENCIES[edition]

    @staticmethod
    def get_exclude_patterns(edition: AstraEdition) -> List[str]:
        """Get the list of file patterns to exclude for a specific edition."""
        return InstallerConfig.EXCLUDE_PATTERNS[edition] 