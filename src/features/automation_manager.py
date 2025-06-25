import os
import json
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import schedule
import threading
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from geopy.geocoder import Nominatim
from plyer import notification
import pytesseract
import cv2
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ..core.intent_recognizer import IntentRecognizer
from ..core.feature_manager import BaseFeature
from ..ai.deepseek_client import DeepSeekClient

@dataclass
class MacroAction:
    feature_name: str
    command: str
    parameters: Dict[str, any]

@dataclass
class Macro:
    name: str
    trigger_phrase: str
    description: str
    actions: List[MacroAction]
    schedule: Optional[str] = None  # Cron-style schedule
    location_trigger: Optional[str] = None
    time_trigger: Optional[str] = None
    activity_trigger: Optional[str] = None

@dataclass
class NotificationRule:
    title: str
    message: str
    conditions: Dict[str, any]
    priority: str = "normal"
    timeout: int = 10

class AutomationManager(BaseFeature):
    def __init__(self, intent_recognizer: IntentRecognizer, ai_client: DeepSeekClient):
        super().__init__("automation_manager")
        self.intent_recognizer = intent_recognizer
        self.ai_client = ai_client
        self.macros: Dict[str, Macro] = {}
        self.notification_rules: List[NotificationRule] = []
        self.observer = Observer()
        self.load_configurations()
        self._setup_watchers()
        self._start_scheduler()
        
        # Initialize OCR
        try:
            self.tesseract_cmd = pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except Exception as e:
            logging.warning(f"Tesseract not found on Windows path: {e}")
            # Try common Unix paths
            unix_paths = ['/usr/bin/tesseract', '/usr/local/bin/tesseract']
            for path in unix_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

    def load_configurations(self):
        """Load macros and notification rules from configuration files"""
        config_dir = Path("config/automation")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load macros
        macro_file = config_dir / "macros.json"
        if macro_file.exists():
            with open(macro_file, "r") as f:
                macro_data = json.load(f)
                for macro_dict in macro_data:
                    actions = [MacroAction(**action) for action in macro_dict.pop("actions")]
                    macro = Macro(**macro_dict, actions=actions)
                    self.macros[macro.name] = macro

        # Load notification rules
        rules_file = config_dir / "notification_rules.json"
        if rules_file.exists():
            with open(rules_file, "r") as f:
                rules_data = json.load(f)
                self.notification_rules = [NotificationRule(**rule) for rule in rules_data]

    def save_configurations(self):
        """Save current macros and notification rules to configuration files"""
        config_dir = Path("config/automation")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Save macros
        with open(config_dir / "macros.json", "w") as f:
            macro_data = [asdict(macro) for macro in self.macros.values()]
            json.dump(macro_data, f, indent=2)
            
        # Save notification rules
        with open(config_dir / "notification_rules.json", "w") as f:
            rules_data = [asdict(rule) for rule in self.notification_rules]
            json.dump(rules_data, f, indent=2)

    def create_macro(self, name: str, trigger_phrase: str, actions: List[MacroAction], 
                    schedule: Optional[str] = None, location: Optional[str] = None,
                    time_trigger: Optional[str] = None, activity: Optional[str] = None) -> Macro:
        """Create a new voice macro with specified triggers and actions"""
        macro = Macro(
            name=name,
            trigger_phrase=trigger_phrase,
            description=f"Custom macro: {name}",
            actions=actions,
            schedule=schedule,
            location_trigger=location,
            time_trigger=time_trigger,
            activity_trigger=activity
        )
        self.macros[name] = macro
        self.save_configurations()
        
        # Set up schedule if provided
        if schedule:
            self._schedule_macro(macro)
            
        return macro

    def execute_macro(self, macro_name: str) -> bool:
        """Execute a specific macro by name"""
        if macro_name not in self.macros:
            return False
            
        macro = self.macros[macro_name]
        try:
            for action in macro.actions:
                # Get the feature instance from feature manager
                feature = self.feature_manager.get_feature(action.feature_name)
                if feature:
                    # Execute the command with parameters
                    method = getattr(feature, action.command, None)
                    if method:
                        method(**action.parameters)
                    else:
                        logging.error(f"Command {action.command} not found in feature {action.feature_name}")
                else:
                    logging.error(f"Feature {action.feature_name} not found")
            return True
        except Exception as e:
            logging.error(f"Error executing macro {macro_name}: {e}")
            return False

    def add_notification_rule(self, title: str, message: str, conditions: Dict[str, any],
                            priority: str = "normal", timeout: int = 10) -> NotificationRule:
        """Add a new smart notification rule"""
        rule = NotificationRule(title, message, conditions, priority, timeout)
        self.notification_rules.append(rule)
        self.save_configurations()
        return rule

    def check_notification_conditions(self, rule: NotificationRule) -> bool:
        """Check if notification conditions are met"""
        for condition_type, condition_value in rule.conditions.items():
            if condition_type == "time":
                current_time = datetime.now().strftime("%H:%M")
                if current_time != condition_value:
                    return False
            elif condition_type == "location":
                # Use geopy to check location
                geolocator = Nominatim(user_agent="astra_assistant")
                try:
                    current_location = geolocator.geocode("current location")
                    if current_location != condition_value:
                        return False
                except Exception as e:
                    logging.error(f"Error checking location: {e}")
                    return False
            elif condition_type == "activity":
                # Check user activity (implement activity detection logic)
                current_activity = self._detect_current_activity()
                if current_activity != condition_value:
                    return False
        return True

    def send_notification(self, title: str, message: str, priority: str = "normal", timeout: int = 10):
        """Send a system notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
                timeout=timeout,
            )
        except Exception as e:
            logging.error(f"Error sending notification: {e}")

    def extract_data_from_image(self, image_path: str, template: Optional[str] = None) -> Dict[str, any]:
        """Extract data from image using OCR"""
        try:
            # Read image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image at {image_path}")

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply thresholding to preprocess the image
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # Perform OCR
            text = pytesseract.image_to_string(gray)

            # If template is provided, use it to structure the extracted data
            if template:
                return self._parse_text_with_template(text, template)
            
            return {"raw_text": text}

        except Exception as e:
            logging.error(f"Error extracting data from image: {e}")
            return {}

    def _parse_text_with_template(self, text: str, template: str) -> Dict[str, any]:
        """Parse extracted text according to template"""
        try:
            # Use AI to help structure the data
            prompt = f"Extract structured data from this text according to template {template}:\n{text}"
            response = self.ai_client.get_response(prompt)
            
            # Convert AI response to structured data
            # This is a simplified version - enhance based on actual AI response format
            structured_data = json.loads(response)
            return structured_data
        except Exception as e:
            logging.error(f"Error parsing text with template: {e}")
            return {"raw_text": text}

    def export_to_spreadsheet(self, data: List[Dict[str, any]], output_path: str):
        """Export extracted data to spreadsheet"""
        try:
            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False)
            return True
        except Exception as e:
            logging.error(f"Error exporting to spreadsheet: {e}")
            return False

    def _setup_watchers(self):
        """Set up file system watchers for automation triggers"""
        class AutomationEventHandler(FileSystemEventHandler):
            def __init__(self, automation_manager):
                self.automation_manager = automation_manager

            def on_modified(self, event):
                if not event.is_directory:
                    self.automation_manager._handle_file_change(event.src_path)

        # Watch configured directories
        watch_dirs = self._get_watch_directories()
        for directory in watch_dirs:
            self.observer.schedule(AutomationEventHandler(self), directory, recursive=False)
        self.observer.start()

    def _start_scheduler(self):
        """Start the scheduler for time-based automations"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)

        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

    def _schedule_macro(self, macro: Macro):
        """Schedule a macro based on its triggers"""
        if macro.schedule:
            schedule.every().day.at(macro.schedule).do(self.execute_macro, macro.name)

    def _detect_current_activity(self) -> str:
        """Detect current user activity"""
        # Implement activity detection logic
        # This could involve checking active windows, system state, etc.
        return "unknown"

    def _get_watch_directories(self) -> List[str]:
        """Get list of directories to watch for changes"""
        # Implement logic to get watch directories from configuration
        return ["downloads", "documents"]  # Example directories

    def _handle_file_change(self, file_path: str):
        """Handle file system changes for automation"""
        # Implement file change handling logic
        logging.info(f"File changed: {file_path}")
        # Check if any automation rules apply to this change
        # Execute relevant macros or notifications

    def handle_voice_command(self, command: str) -> Union[str, bool]:
        """Handle voice commands for automation"""
        try:
            # Check if command matches any macro trigger phrases
            for macro in self.macros.values():
                if command.lower() in macro.trigger_phrase.lower():
                    success = self.execute_macro(macro.name)
                    return "Macro executed successfully" if success else "Failed to execute macro"

            # If no direct match, use AI to understand the intent
            response = self.ai_client.get_response(
                f"Interpret this automation command: {command}"
            )
            
            # Process the AI response and take appropriate action
            # This is a simplified version - enhance based on actual needs
            return response

        except Exception as e:
            logging.error(f"Error handling voice command: {e}")
            return False

    def cleanup(self):
        """Cleanup resources"""
        self.observer.stop()
        self.observer.join()
        self.save_configurations() 