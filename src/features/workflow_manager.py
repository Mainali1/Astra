import os
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import asyncio
from datetime import datetime, timedelta
import schedule
from rocketry import Rocketry
from rocketry.conds import daily, hourly, monthly, weekly

from ..core.intent_recognizer import IntentRecognizer
from ..core.feature_manager import BaseFeature
from ..ai.deepseek_client import DeepSeekClient

@dataclass
class WorkflowStep:
    name: str
    action: str
    parameters: Dict[str, any]
    condition: Optional[str] = None
    retry_count: int = 0
    timeout: Optional[int] = None
    on_success: Optional[str] = None
    on_failure: Optional[str] = None

@dataclass
class Workflow:
    name: str
    description: str
    trigger_type: str  # voice, schedule, event
    trigger_value: str
    steps: List[WorkflowStep]
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

class WorkflowManager(BaseFeature):
    def __init__(self, intent_recognizer: IntentRecognizer, ai_client: DeepSeekClient):
        super().__init__("workflow_manager")
        self.intent_recognizer = intent_recognizer
        self.ai_client = ai_client
        self.workflows: Dict[str, Workflow] = {}
        self.app = Rocketry(execution="async")
        self.load_workflows()
        self._setup_scheduler()

    def load_workflows(self):
        """Load workflows from configuration file"""
        config_dir = Path("config/workflows")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = config_dir / "workflows.json"
        if workflow_file.exists():
            with open(workflow_file, "r") as f:
                workflow_data = json.load(f)
                for wf_dict in workflow_data:
                    steps = [WorkflowStep(**step) for step in wf_dict.pop("steps")]
                    workflow = Workflow(**wf_dict, steps=steps)
                    self.workflows[workflow.name] = workflow
                    self._register_workflow(workflow)

    def save_workflows(self):
        """Save workflows to configuration file"""
        config_dir = Path("config/workflows")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_dir / "workflows.json", "w") as f:
            workflow_data = [asdict(wf) for wf in self.workflows.values()]
            json.dump(workflow_data, f, indent=2)

    def create_workflow(self, name: str, description: str, trigger_type: str,
                       trigger_value: str, steps: List[WorkflowStep]) -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(
            name=name,
            description=description,
            trigger_type=trigger_type,
            trigger_value=trigger_value,
            steps=steps
        )
        self.workflows[name] = workflow
        self._register_workflow(workflow)
        self.save_workflows()
        return workflow

    def _register_workflow(self, workflow: Workflow):
        """Register workflow with the scheduler"""
        if workflow.trigger_type == "schedule":
            @self.app.task(workflow.trigger_value)
            async def scheduled_workflow():
                await self.execute_workflow(workflow.name)

        elif workflow.trigger_type == "event":
            # Register event-based trigger
            self._register_event_trigger(workflow)

    def _register_event_trigger(self, workflow: Workflow):
        """Register event-based trigger for workflow"""
        event_type = workflow.trigger_value
        
        if event_type.startswith("file:"):
            # File system event trigger
            path = event_type.split(":")[1]
            self._watch_file_path(path, workflow.name)
            
        elif event_type.startswith("time:"):
            # Time-based trigger
            time_spec = event_type.split(":")[1]
            schedule.every().day.at(time_spec).do(
                lambda: asyncio.run(self.execute_workflow(workflow.name))
            )

    async def execute_workflow(self, workflow_name: str) -> bool:
        """Execute a workflow by name"""
        if workflow_name not in self.workflows:
            return False
            
        workflow = self.workflows[workflow_name]
        if not workflow.enabled:
            return False

        workflow.last_run = datetime.now()
        try:
            for step in workflow.steps:
                success = await self._execute_step(step)
                if not success:
                    if step.on_failure:
                        await self._handle_failure(step)
                    return False
                if step.on_success:
                    await self._handle_success(step)
            
            return True
        except Exception as e:
            logging.error(f"Error executing workflow {workflow_name}: {e}")
            return False
        finally:
            self._update_next_run(workflow)
            self.save_workflows()

    async def _execute_step(self, step: WorkflowStep) -> bool:
        """Execute a single workflow step"""
        try:
            if step.condition and not self._evaluate_condition(step.condition):
                return True  # Skip step but don't count as failure

            # Get the appropriate feature and method
            feature_name, method_name = step.action.split(".")
            feature = self.feature_manager.get_feature(feature_name)
            if not feature:
                raise ValueError(f"Feature {feature_name} not found")

            method = getattr(feature, method_name, None)
            if not method:
                raise ValueError(f"Method {method_name} not found in feature {feature_name}")

            # Execute with timeout if specified
            if step.timeout:
                async with asyncio.timeout(step.timeout):
                    result = await self._execute_with_retry(method, step)
            else:
                result = await self._execute_with_retry(method, step)

            return result
        except Exception as e:
            logging.error(f"Error executing step {step.name}: {e}")
            return False

    async def _execute_with_retry(self, method: Callable, step: WorkflowStep) -> bool:
        """Execute a method with retry logic"""
        for attempt in range(step.retry_count + 1):
            try:
                if asyncio.iscoroutinefunction(method):
                    result = await method(**step.parameters)
                else:
                    result = method(**step.parameters)
                return True if result is None else bool(result)
            except Exception as e:
                if attempt < step.retry_count:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition string"""
        try:
            # Use AI to evaluate complex conditions
            response = self.ai_client.get_response(
                f"Evaluate this condition in the current context: {condition}"
            )
            return response.lower() == "true"
        except Exception as e:
            logging.error(f"Error evaluating condition: {e}")
            return False

    async def _handle_success(self, step: WorkflowStep):
        """Handle successful step execution"""
        if step.on_success.startswith("workflow:"):
            workflow_name = step.on_success.split(":")[1]
            await self.execute_workflow(workflow_name)
        else:
            # Handle other success actions
            pass

    async def _handle_failure(self, step: WorkflowStep):
        """Handle step execution failure"""
        if step.on_failure.startswith("workflow:"):
            workflow_name = step.on_failure.split(":")[1]
            await self.execute_workflow(workflow_name)
        else:
            # Handle other failure actions
            pass

    def _update_next_run(self, workflow: Workflow):
        """Update the next scheduled run for a workflow"""
        if workflow.trigger_type == "schedule":
            # Parse schedule and calculate next run
            schedule_parts = workflow.trigger_value.split()
            if len(schedule_parts) == 5:  # Cron format
                # Implement cron parsing logic
                pass
            else:
                # Handle other schedule formats
                pass

    def _setup_scheduler(self):
        """Set up the task scheduler"""
        async def run_scheduler():
            await self.app.serve()

        asyncio.create_task(run_scheduler())

    def _watch_file_path(self, path: str, workflow_name: str):
        """Set up file system watcher for workflow trigger"""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class WorkflowEventHandler(FileSystemEventHandler):
            def __init__(self, workflow_manager, workflow_name):
                self.workflow_manager = workflow_manager
                self.workflow_name = workflow_name

            def on_modified(self, event):
                if not event.is_directory:
                    asyncio.run(
                        self.workflow_manager.execute_workflow(self.workflow_name)
                    )

        observer = Observer()
        observer.schedule(WorkflowEventHandler(self, workflow_name), path, recursive=False)
        observer.start()

    async def handle_voice_command(self, command: str) -> str:
        """Handle voice commands for workflow management"""
        try:
            # Use AI to interpret the command
            interpretation = self.ai_client.get_response(
                f"Interpret this workflow command: {command}"
            )
            
            # Parse the interpretation and take appropriate action
            if "create" in interpretation.lower():
                # Handle workflow creation
                pass
            elif "run" in interpretation.lower():
                # Handle workflow execution
                pass
            elif "disable" in interpretation.lower():
                # Handle workflow disable
                pass
            elif "enable" in interpretation.lower():
                # Handle workflow enable
                pass
            
            return "Command processed successfully"
        except Exception as e:
            logging.error(f"Error handling voice command: {e}")
            return "Failed to process command"

    def cleanup(self):
        """Cleanup resources"""
        self.save_workflows()
        # Stop any running observers or schedulers 