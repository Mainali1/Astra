
from typing import List, Dict, Any, Callable

class WorkflowManager:
    """
    A basic in-memory workflow manager for defining and executing sequential workflows.
    """
    def __init__(self):
        self.workflows: Dict[str, List[Dict[str, Any]]] = {}

    def define_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]) -> str:
        """
        Defines a new workflow.

        Args:
            workflow_name: The unique name of the workflow.
            steps: A list of dictionaries, where each dictionary represents a step.
                   Each step should have at least a 'name' and 'action' (callable).
                   Example: [{'name': 'step1', 'action': my_function, 'args': [1, 2]}]

        Returns:
            A message indicating the status of the workflow definition.
        """
        if workflow_name in self.workflows:
            return f"Error: Workflow '{workflow_name}' already exists."
        self.workflows[workflow_name] = steps
        return f"Workflow '{workflow_name}' defined successfully with {len(steps)} steps."

    def execute_workflow(self, workflow_name: str, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes a defined workflow.

        Args:
            workflow_name: The name of the workflow to execute.
            initial_context: Initial data to pass to the first step of the workflow.

        Returns:
            A dictionary containing the final context after execution, or an error.
        """
        if workflow_name not in self.workflows:
            return {"status": "error", "message": f"Error: Workflow '{workflow_name}' not found."}

        current_context = initial_context if initial_context is not None else {}
        results = {"status": "success", "steps_executed": []}

        for i, step in enumerate(self.workflows[workflow_name]):
            step_name = step.get('name', f'step_{i+1}')
            action: Callable = step.get('action')
            args = step.get('args', [])
            kwargs = step.get('kwargs', {})

            if not callable(action):
                results["status"] = "error"
                results["message"] = f"Error: Step '{step_name}' has no callable action."
                return results

            try:
                step_output = action(*args, **kwargs, context=current_context) # Pass context to action
                current_context[step_name] = step_output # Update context with step output
                results["steps_executed"].append({"name": step_name, "status": "success", "output": step_output})
            except Exception as e:
                results["status"] = "error"
                results["message"] = f"Error executing step '{step_name}': {e}"
                results["steps_executed"].append({"name": step_name, "status": "failed", "error": str(e)})
                return results

        results["final_context"] = current_context
        return results

    def list_workflows(self) -> List[str]:
        """
        Lists all defined workflows.

        Returns:
            A list of workflow names.
        """
        return list(self.workflows.keys())

workflow_manager = WorkflowManager()
