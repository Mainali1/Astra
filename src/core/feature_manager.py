"""
Enhanced Feature Manager for Astra Voice Assistant
Manages 50+ modular features with dynamic loading and configuration
"""

import os
import json
import importlib
import inspect
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class FeatureInfo:
    """Feature information structure"""
    name: str
    description: str
    category: str
    keywords: List[str]
    examples: List[str]
    enabled: bool = True
    version: str = "1.0.0"
    author: str = "Astra Team"
    dependencies: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    last_updated: Optional[str] = None

class FeatureManager:
    """Manages all voice assistant features"""
    
    def __init__(self, features_dir: str = "src/features"):
        self.features_dir = Path(features_dir)
        self.features: Dict[str, Any] = {}
        self.feature_info: Dict[str, FeatureInfo] = {}
        self.enabled_features: List[str] = []
        self.config_file = Path("data/features_config.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._load_config()
        
        # Initialize feature categories
        self.categories = {
            "productivity": "Productivity tools and utilities",
            "entertainment": "Entertainment and media features",
            "personal": "Personal assistant features",
            "knowledge": "Knowledge and information access",
            "system": "System control and utilities",
            "media": "Media playback and management",
            "context": "Context and learning features",
            "sync": "Synchronization and data management",
            "automation": "Automation and workflow features"
        }
        
        # Load all features
        self._load_features()
    
    def _load_config(self):
        """Load feature configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.enabled_features = config.get('enabled_features', [])
            except (json.JSONDecodeError, IOError):
                self.enabled_features = []
        else:
            self.enabled_features = []
    
    def _save_config(self):
        """Save feature configuration to file"""
        config = {
            'enabled_features': self.enabled_features,
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving feature config: {e}")
    
    def _load_features(self):
        """Load all available features"""
        # Core features that are always available
        core_features = {
            'weather': {
                'name': 'weather',
                'description': 'Get weather information for any location',
                'category': 'knowledge',
                'keywords': ['weather', 'temperature', 'forecast', 'climate'],
                'examples': [
                    'What\'s the weather like?',
                    'Weather forecast for tomorrow',
                    'Temperature in New York'
                ]
            },
            'time': {
                'name': 'time',
                'description': 'Get current time and date information',
                'category': 'productivity',
                'keywords': ['time', 'date', 'clock', 'schedule'],
                'examples': [
                    'What time is it?',
                    'What\'s today\'s date?',
                    'Time in different timezones'
                ]
            },
            'calculator': {
                'name': 'calculator',
                'description': 'Perform mathematical calculations',
                'category': 'productivity',
                'keywords': ['calculate', 'math', 'equation', 'compute'],
                'examples': [
                    'Calculate 15 plus 27',
                    'What is 25 times 4?',
                    'Solve 2x + 5 = 15'
                ]
            },
            'notes': {
                'name': 'notes',
                'description': 'Create, search, and manage text notes with tags',
                'category': 'productivity',
                'keywords': ['note', 'notes', 'write', 'create', 'search', 'find', 'delete', 'tag'],
                'examples': [
                    'Create a note titled "Meeting Notes" about the project discussion',
                    'Find notes about weather',
                    'Show my notes'
                ]
            },
            'reminder': {
                'name': 'reminder',
                'description': 'Set, manage, and check reminders with natural language time parsing',
                'category': 'productivity',
                'keywords': ['reminder', 'remind', 'alarm', 'schedule', 'due', 'time'],
                'examples': [
                    'Set reminder for meeting at 3 PM',
                    'Remind me to call mom in 2 hours',
                    'Show my reminders'
                ]
            },
            'dictionary': {
                'name': 'dictionary',
                'description': 'Look up word definitions, synonyms, and examples',
                'category': 'knowledge',
                'keywords': ['dictionary', 'define', 'definition', 'meaning', 'synonym', 'antonym', 'word'],
                'examples': [
                    'Define the word "serendipity"',
                    'What does "ephemeral" mean?',
                    'Find synonyms for "happy"',
                    'Look up "ubiquitous" in the dictionary'
                ]
            },
            'converter': {
                'name': 'converter',
                'description': 'Convert between different units of measurement, temperature, currency, and more',
                'category': 'productivity',
                'keywords': ['convert', 'conversion', 'temperature', 'length', 'weight', 'currency', 'units'],
                'examples': [
                    'Convert 100 degrees Fahrenheit to Celsius',
                    'How many meters in 5 feet?',
                    'Convert 50 dollars to euros',
                    'What is 2.5 kilograms in pounds?'
                ]
            },
            'news': {
                'name': 'news',
                'description': 'Get latest news from multiple sources with intelligent categorization',
                'category': 'knowledge',
                'keywords': ['news', 'headlines', 'current events', 'latest', 'breaking', 'top stories'],
                'examples': [
                    'What\'s the latest news?',
                    'Show me breaking news',
                    'News about technology',
                    'Top headlines today',
                    'Business news',
                    'Sports news'
                ]
            },
            'translation': {
                'name': 'translation',
                'description': 'Translate text between 50+ languages using multiple free APIs',
                'category': 'communication',
                'keywords': ['translate', 'translation', 'language', 'interpret', 'convert'],
                'examples': [
                    'Translate hello to Spanish',
                    'What is bonjour in English?',
                    'Translate this text to French',
                    'How do you say thank you in German?',
                    'Translate from English to Japanese'
                ]
            },
            'music': {
                'name': 'music',
                'description': 'Play music from local files and streaming services using free APIs',
                'category': 'entertainment',
                'keywords': ['music', 'play', 'song', 'artist', 'album', 'playlist', 'spotify', 'youtube'],
                'examples': [
                    'Play some music',
                    'Play Bohemian Rhapsody',
                    'Search for Queen songs',
                    'Create a playlist'
                ]
            },
            'jokes': {
                'name': 'jokes',
                'description': 'Tell jokes and provide humor with mood-based recommendations',
                'category': 'entertainment',
                'keywords': ['joke', 'jokes', 'funny', 'humor', 'laugh', 'comedy'],
                'examples': [
                    'Tell me a joke',
                    'Tell a programming joke',
                    'Make me laugh',
                    'Joke about cats'
                ]
            },
            'todo': {
                'name': 'todo',
                'description': 'Comprehensive task management with categories, priorities, and due dates',
                'category': 'productivity',
                'keywords': ['todo', 'task', 'tasks', 'add task', 'list tasks', 'complete task', 'delete task'],
                'examples': [
                    'Add task buy groceries',
                    'Add task call mom high priority',
                    'Add task finish report in work due tomorrow',
                    'List tasks',
                    'Complete task buy groceries',
                    'Task stats'
                ]
            },
            'wikipedia': {
                'name': 'wikipedia',
                'description': 'Search Wikipedia articles and get summaries using free API',
                'category': 'knowledge',
                'keywords': ['wikipedia', 'wiki', 'search', 'what is', 'who is', 'tell me about'],
                'examples': [
                    'Search for artificial intelligence',
                    'What is machine learning?',
                    'Tell me about Python programming',
                    'Random article',
                    'Featured article'
                ]
            },
            'timer': {
                'name': 'timer',
                'description': 'Stopwatch, countdown timers, and Pomodoro timer with voice commands',
                'category': 'productivity',
                'keywords': ['timer', 'stopwatch', 'countdown', 'pomodoro', 'start timer', 'stop timer'],
                'examples': [
                    'Start stopwatch',
                    'Set timer for 5 minutes',
                    'Start pomodoro',
                    'Stop timer',
                    'Timer status'
                ]
            },
            'file_manager': {
                'name': 'file_manager',
                'description': 'Browse, search, and manage files on the local system',
                'category': 'system',
                'keywords': ['files', 'folders', 'list files', 'search files', 'create folder'],
                'examples': [
                    'List files',
                    'Go to Documents folder',
                    'Search for report.pdf',
                    'Create folder project_files',
                    'Where am i'
                ]
            },
            'system_monitor': {
                'name': 'system_monitor',
                'description': 'Monitor CPU, memory, disk, and network usage with health assessment',
                'category': 'system',
                'keywords': ['cpu', 'memory', 'disk', 'network', 'system health', 'performance'],
                'examples': [
                    'CPU usage',
                    'Memory usage',
                    'System health',
                    'Disk usage',
                    'Top processes'
                ]
            },
            'summarizer': {
                'name': 'summarizer',
                'description': 'Enhanced document and text summarization with AI analysis',
                'category': 'productivity',
                'keywords': ['summarize', 'summary', 'document', 'text', 'analyze'],
                'examples': [
                    'Summarize this document',
                    'Give me a summary of this PDF',
                    'Analyze this text',
                    'Extract key points from this file'
                ]
            },
            'calendar': {
                'name': 'calendar',
                'description': 'Manage events, appointments, and schedules with voice commands',
                'category': 'productivity',
                'keywords': ['calendar', 'event', 'events', 'schedule', 'appointment', 'meeting'],
                'examples': [
                    'Add event team meeting at 3 PM',
                    'Schedule doctor appointment tomorrow',
                    'Events today',
                    'This week\'s events',
                    'Show calendar'
                ]
            },
            'project_manager': {
                'name': 'project_manager',
                'description': 'AI-driven project management with planning, brainstorming, and risk analysis',
                'enabled': True,
                'requires_network': True,
                'handler': 'src.features.project_manager.handle_project_command',
                'keywords': ['project', 'plan', 'brainstorm', 'schedule', 'risks'],
                'examples': [
                    'Plan a new software project',
                    'Brainstorm ideas for marketing campaign',
                    'Optimize my task schedule',
                    'Analyze project risks'
                ]
            },
            'email_manager': {
                'name': 'email_manager',
                'description': 'AI-powered email management with summarization and prioritization',
                'enabled': True,
                'requires_network': True,
                'handler': 'src.features.email_manager.handle_email_command',
                'keywords': ['email', 'mail', 'inbox', 'summarize', 'prioritize'],
                'examples': [
                    'Summarize my recent emails',
                    'Generate response to last email',
                    'Prioritize my inbox',
                    'Check important emails'
                ]
            },
            'automation_manager': {
                'name': 'automation_manager',
                'description': 'Create and manage voice-controlled macros and automated workflows',
                'category': 'automation',
                'keywords': ['automation', 'macro', 'workflow', 'routine', 'script', 'automate'],
                'examples': [
                    'Create a morning routine macro',
                    'Start my work mode',
                    'Run backup script',
                    'Show my automation workflows',
                    'Create new automation'
                ]
            },
            'workflow_manager': {
                'name': 'workflow_manager',
                'description': 'Manage complex automation workflows with multiple steps and conditions',
                'category': 'automation',
                'keywords': ['workflow', 'process', 'steps', 'sequence', 'automation'],
                'examples': [
                    'Create document processing workflow',
                    'Run invoice processing workflow',
                    'Show active workflows',
                    'Enable workflow notifications'
                ]
            },
            'script_manager': {
                'name': 'script_manager',
                'description': 'Create and manage voice-controlled scripts and system automation',
                'category': 'automation',
                'keywords': ['script', 'command', 'system', 'automate', 'run'],
                'examples': [
                    'Create backup script',
                    'Run system cleanup',
                    'Show available scripts',
                    'Create new script'
                ]
            }
        }
        
        # Register all core features
        for name, info in core_features.items():
            self._register_feature(name, info)
        
        # Load additional feature modules
        self._load_feature_modules()
        
        # Enable configured features
        self._enable_configured_features()
    
    def _load_feature_modules(self):
        """Load feature modules from the features directory"""
        if not self.features_dir.exists():
            return
        
        for feature_file in self.features_dir.glob("*.py"):
            if feature_file.name.startswith("__"):
                continue
            
            feature_name = feature_file.stem
            try:
                # Import the feature module
                module = importlib.import_module(f"features.{feature_name}")
                
                # Look for FEATURE_INFO in the module
                if hasattr(module, 'FEATURE_INFO'):
                    info = module.FEATURE_INFO
                    self._register_feature(feature_name, info)
                    
                    # Look for handler function
                    handler_name = f"handle_{feature_name}_command"
                    if hasattr(module, handler_name):
                        handler = getattr(module, handler_name)
                        self.features[feature_name] = handler
                
            except ImportError as e:
                print(f"Error loading feature {feature_name}: {e}")
    
    def _register_feature(self, name: str, info: Dict[str, Any]):
        """Register a feature with the manager"""
        feature_info = FeatureInfo(
            name=name,
            description=info.get('description', ''),
            category=info.get('category', 'system'),
            keywords=info.get('keywords', []),
            examples=info.get('examples', []),
            enabled=name in self.enabled_features,
            version=info.get('version', '1.0.0'),
            author=info.get('author', 'Astra Team'),
            dependencies=info.get('dependencies', []),
            config=info.get('config', {}),
            last_updated=datetime.now().isoformat()
        )
        
        self.feature_info[name] = feature_info
    
    def _enable_configured_features(self):
        """Enable features based on configuration"""
        for feature_name in self.enabled_features:
            if feature_name in self.feature_info:
                self.feature_info[feature_name].enabled = True
    
    def get_feature(self, name: str) -> Optional[Any]:
        """Get a specific feature handler"""
        return self.features.get(name)
    
    def get_feature_info(self, name: str) -> Optional[FeatureInfo]:
        """Get information about a specific feature"""
        return self.feature_info.get(name)
    
    def list_features(self, category: Optional[str] = None) -> List[FeatureInfo]:
        """List all features, optionally filtered by category"""
        features = list(self.feature_info.values())
        
        if category:
            features = [f for f in features if f.category == category]
        
        return sorted(features, key=lambda x: x.name)
    
    def get_features_by_category(self) -> Dict[str, List[FeatureInfo]]:
        """Get features organized by category"""
        categorized = {}
        for feature in self.feature_info.values():
            if feature.category not in categorized:
                categorized[feature.category] = []
            categorized[feature.category].append(feature)
        
        return categorized
    
    def enable_feature(self, name: str) -> bool:
        """Enable a feature"""
        if name in self.feature_info:
            self.feature_info[name].enabled = True
            if name not in self.enabled_features:
                self.enabled_features.append(name)
            self._save_config()
            return True
        return False
    
    def disable_feature(self, name: str) -> bool:
        """Disable a feature"""
        if name in self.feature_info:
            self.feature_info[name].enabled = False
            if name in self.enabled_features:
                self.enabled_features.remove(name)
            self._save_config()
            return True
        return False
    
    def is_feature_enabled(self, name: str) -> bool:
        """Check if a feature is enabled"""
        return name in self.enabled_features
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled features"""
        return self.enabled_features.copy()
    
    def search_features(self, query: str) -> List[FeatureInfo]:
        """Search features by name, description, or keywords"""
        query = query.lower()
        results = []
        
        for feature in self.feature_info.values():
            if (query in feature.name.lower() or
                query in feature.description.lower() or
                any(query in keyword.lower() for keyword in feature.keywords)):
                results.append(feature)
        
        return results
    
    def get_feature_statistics(self) -> Dict[str, Any]:
        """Get statistics about features"""
        total_features = len(self.feature_info)
        enabled_features = len(self.enabled_features)
        
        category_counts = {}
        for feature in self.feature_info.values():
            category = feature.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'total_features': total_features,
            'enabled_features': enabled_features,
            'disabled_features': total_features - enabled_features,
            'categories': category_counts,
            'last_updated': datetime.now().isoformat()
        }
    
    def execute_feature(self, feature_name: str, *args, **kwargs) -> Any:
        """Execute a feature handler"""
        if not self.is_feature_enabled(feature_name):
            raise ValueError(f"Feature '{feature_name}' is not enabled")
        
        handler = self.get_feature(feature_name)
        if not handler:
            raise ValueError(f"Feature '{feature_name}' has no handler")
        
        return handler(*args, **kwargs)
    
    def get_feature_suggestions(self, user_input: str) -> List[str]:
        """Get feature suggestions based on user input"""
        suggestions = []
        user_input_lower = user_input.lower()
        
        for feature in self.feature_info.values():
            if not feature.enabled:
                continue
            
            # Check if any keywords match
            for keyword in feature.keywords:
                if keyword.lower() in user_input_lower:
                    suggestions.extend(feature.examples[:2])  # Top 2 examples
                    break
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def export_config(self) -> Dict[str, Any]:
        """Export current feature configuration"""
        return {
            'enabled_features': self.enabled_features,
            'feature_info': {name: asdict(info) for name, info in self.feature_info.items()},
            'categories': self.categories,
            'statistics': self.get_feature_statistics(),
            'exported_at': datetime.now().isoformat()
        }
    
    def import_config(self, config: Dict[str, Any]) -> bool:
        """Import feature configuration"""
        try:
            if 'enabled_features' in config:
                self.enabled_features = config['enabled_features']
                self._save_config()
                self._enable_configured_features()
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False

# Global feature manager instance
feature_manager = FeatureManager()

def get_feature_manager() -> FeatureManager:
    """Get the global feature manager instance"""
    return feature_manager 