import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
import subprocess
import shlex
import sys
from datetime import datetime

from ..core.intent_recognizer import IntentRecognizer
from ..core.feature_manager import BaseFeature
from ..ai.deepseek_client import DeepSeekClient

@dataclass
class Script:
    name: str
    description: str
    command: str
    working_directory: Optional[str] = None
    environment_vars: Optional[Dict[str, str]] = None
    voice_triggers: List[str] = None
    schedule: Optional[str] = None
    enabled: bool = True
    platform: Optional[str] = None  # windows, linux, darwin, or None for all
    last_run: Optional[datetime] = None
    timeout: Optional[int] = None
    requires_confirmation: bool = False

class ScriptManager(BaseFeature):
    def __init__(self, intent_recognizer: IntentRecognizer, ai_client: DeepSeekClient):
        super().__init__("script_manager")
        self.intent_recognizer = intent_recognizer
        self.ai_client = ai_client
        self.scripts: Dict[str, Script] = {}
        self.script_dir = Path("scripts")
        self.script_dir.mkdir(parents=True, exist_ok=True)
        self.load_scripts()

    def load_scripts(self):
        """Load scripts from configuration file"""
        config_file = self.script_dir / "scripts.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                script_data = json.load(f)
                for script_dict in script_data:
                    script = Script(**script_dict)
                    if self._is_platform_compatible(script):
                        self.scripts[script.name] = script

    def save_scripts(self):
        """Save scripts to configuration file"""
        config_file = self.script_dir / "scripts.json"
        with open(config_file, "w") as f:
            script_data = [asdict(script) for script in self.scripts.values()]
            json.dump(script_data, f, indent=2)

    def create_script(self, name: str, description: str, command: str,
                     working_directory: Optional[str] = None,
                     environment_vars: Optional[Dict[str, str]] = None,
                     voice_triggers: List[str] = None,
                     schedule: Optional[str] = None,
                     platform: Optional[str] = None,
                     timeout: Optional[int] = None,
                     requires_confirmation: bool = False) -> Script:
        """Create a new script"""
        script = Script(
            name=name,
            description=description,
            command=command,
            working_directory=working_directory,
            environment_vars=environment_vars or {},
            voice_triggers=voice_triggers or [],
            schedule=schedule,
            platform=platform,
            timeout=timeout,
            requires_confirmation=requires_confirmation
        )
        
        if self._is_platform_compatible(script):
            self.scripts[name] = script
            self.save_scripts()
            return script
        else:
            raise ValueError(f"Script not compatible with current platform: {sys.platform}")

    def _is_platform_compatible(self, script: Script) -> bool:
        """Check if script is compatible with current platform"""
        if script.platform is None:
            return True
        return script.platform == sys.platform

    async def execute_script(self, script_name: str, confirm: bool = False) -> Union[str, bool]:
        """Execute a script by name"""
        if script_name not in self.scripts:
            return False
            
        script = self.scripts[script_name]
        if not script.enabled:
            return False

        if script.requires_confirmation and not confirm:
            return "confirmation_required"

        try:
            # Prepare environment
            env = os.environ.copy()
            if script.environment_vars:
                env.update(script.environment_vars)

            # Prepare working directory
            work_dir = script.working_directory or os.getcwd()

            # Split command into arguments
            if sys.platform == "win32":
                args = script.command  # Windows needs the full string
            else:
                args = shlex.split(script.command)

            # Execute with timeout if specified
            process = await asyncio.create_subprocess_shell(
                script.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=work_dir,
                shell=True
            )

            try:
                if script.timeout:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), 
                        timeout=script.timeout
                    )
                else:
                    stdout, stderr = await process.communicate()

                script.last_run = datetime.now()
                self.save_scripts()

                if process.returncode != 0:
                    logging.error(f"Script {script_name} failed: {stderr.decode()}")
                    return False

                return stdout.decode()

            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                logging.error(f"Script {script_name} timed out")
                return False

        except Exception as e:
            logging.error(f"Error executing script {script_name}: {e}")
            return False

    def get_script_by_trigger(self, trigger: str) -> Optional[Script]:
        """Find a script by its voice trigger"""
        for script in self.scripts.values():
            if script.voice_triggers and any(
                trigger.lower() in t.lower() for t in script.voice_triggers
            ):
                return script
        return None

    async def handle_voice_command(self, command: str) -> str:
        """Handle voice commands for script execution"""
        try:
            # First try direct trigger matching
            script = self.get_script_by_trigger(command)
            if script:
                result = await self.execute_script(script.name)
                if result == "confirmation_required":
                    return "This script requires confirmation. Please confirm to proceed."
                return "Script executed successfully" if result else "Script execution failed"

            # If no direct match, use AI to interpret the command
            interpretation = await self.ai_client.get_response(
                f"Interpret this script command: {command}"
            )
            
            # Parse the interpretation and take appropriate action
            if "create" in interpretation.lower():
                # Extract script details from command using AI
                script_details = await self.ai_client.get_response(
                    f"Extract script creation details from: {command}\n"
                    "Format: {name, description, command}"
                )
                details = json.loads(script_details)
                self.create_script(**details)
                return "Script created successfully"
                
            elif "run" in interpretation.lower():
                # Extract script name from command using AI
                script_name = await self.ai_client.get_response(
                    f"Extract script name from: {command}"
                )
                result = await self.execute_script(script_name)
                if result == "confirmation_required":
                    return "This script requires confirmation. Please confirm to proceed."
                return "Script executed successfully" if result else "Script execution failed"
                
            elif "list" in interpretation.lower():
                scripts = "\n".join(f"- {s.name}: {s.description}" for s in self.scripts.values())
                return f"Available scripts:\n{scripts}"
                
            elif "delete" in interpretation.lower():
                # Extract script name from command using AI
                script_name = await self.ai_client.get_response(
                    f"Extract script name from: {command}"
                )
                if script_name in self.scripts:
                    del self.scripts[script_name]
                    self.save_scripts()
                    return f"Script {script_name} deleted"
                return f"Script {script_name} not found"
                
            return "Command not recognized"
            
        except Exception as e:
            logging.error(f"Error handling voice command: {e}")
            return "Failed to process command"

    def cleanup(self):
        """Cleanup resources"""
        self.save_scripts() 