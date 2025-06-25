"""
AI-driven project management feature for Astra
"""
from datetime import datetime
from typing import Dict, List, Optional
import json
import os

from src.ai.deepseek_client import DeepSeekClient

class ProjectManager:
    def __init__(self):
        self.client = DeepSeekClient()
        self.data_dir = os.path.join(os.path.dirname(__file__), '../../data/projects')
        os.makedirs(self.data_dir, exist_ok=True)
        
    async def generate_project_plan(self, project_description: str) -> Dict:
        """Generate a project plan using AI"""
        prompt = f"""As a project management expert, create a detailed project plan for the following project:

{project_description}

Include:
1. Project objectives
2. Key milestones
3. Timeline estimates
4. Resource requirements
5. Potential risks and mitigation strategies
6. Success metrics

Format the response as a JSON object with these sections."""

        response = await self.client.generate_response(prompt)
        try:
            return json.loads(response)
        except:
            return {"error": "Failed to generate project plan"}

    async def brainstorm_ideas(self, topic: str, context: Optional[str] = None) -> List[Dict]:
        """Generate ideas and suggestions for a topic"""
        context_prompt = f"\nContext: {context}" if context else ""
        prompt = f"""Help me brainstorm ideas for the following topic:

Topic: {topic}{context_prompt}

Generate:
1. Main ideas
2. Related concepts
3. Potential approaches
4. Questions to explore
5. Resources needed

Format the response as a JSON array of idea objects."""

        response = await self.client.generate_response(prompt)
        try:
            return json.loads(response)
        except:
            return [{"error": "Failed to generate ideas"}]

    async def schedule_optimizer(self, tasks: List[Dict], constraints: Dict) -> Dict:
        """Optimize task scheduling based on constraints"""
        prompt = f"""As a scheduling expert, optimize the following tasks based on given constraints:

Tasks: {json.dumps(tasks, indent=2)}
Constraints: {json.dumps(constraints, indent=2)}

Provide:
1. Optimized schedule
2. Task dependencies
3. Resource allocation
4. Priority levels
5. Estimated completion times

Format the response as a JSON object."""

        response = await self.client.generate_response(prompt)
        try:
            return json.loads(response)
        except:
            return {"error": "Failed to optimize schedule"}

    async def analyze_project_risks(self, project_data: Dict) -> List[Dict]:
        """Analyze project risks and provide mitigation strategies"""
        prompt = f"""Analyze the following project data and identify potential risks:

Project Data: {json.dumps(project_data, indent=2)}

For each identified risk:
1. Risk description
2. Impact level
3. Probability
4. Mitigation strategies
5. Contingency plans

Format the response as a JSON array of risk objects."""

        response = await self.client.generate_response(prompt)
        try:
            return json.loads(response)
        except:
            return [{"error": "Failed to analyze risks"}]

class ProjectManagerFeature:
    def __init__(self):
        self.manager = ProjectManager()
        
    async def process_command(self, command: str) -> str:
        """Process project management related commands"""
        if "plan project" in command.lower():
            plan = await self.manager.generate_project_plan(command)
            return self._format_project_plan(plan)
            
        elif "brainstorm" in command.lower():
            ideas = await self.manager.brainstorm_ideas(command)
            return self._format_brainstorm_results(ideas)
            
        elif "optimize schedule" in command.lower():
            # Extract tasks and constraints from command
            # This is a simplified example
            tasks = [{"name": "Task 1", "duration": "2h"}]
            constraints = {"working_hours": "9-5"}
            schedule = await self.manager.schedule_optimizer(tasks, constraints)
            return self._format_schedule(schedule)
            
        elif "analyze risks" in command.lower():
            # Extract project data from command
            project_data = {"name": "Example Project"}
            risks = await self.manager.analyze_project_risks(project_data)
            return self._format_risks(risks)
            
        return "I'm not sure how to help with that project management task."

    def _format_project_plan(self, plan: Dict) -> str:
        """Format project plan for display"""
        if "error" in plan:
            return f"Failed to generate project plan: {plan['error']}"
            
        result = "Project Plan:\n\n"
        for section, content in plan.items():
            result += f"{section.replace('_', ' ').title()}:\n"
            if isinstance(content, list):
                for item in content:
                    result += f"- {item}\n"
            else:
                result += f"{content}\n"
            result += "\n"
        return result

    def _format_brainstorm_results(self, ideas: List[Dict]) -> str:
        """Format brainstorming results for display"""
        if ideas and "error" in ideas[0]:
            return f"Failed to generate ideas: {ideas[0]['error']}"
            
        result = "Brainstorming Results:\n\n"
        for idea in ideas:
            result += f"Idea: {idea.get('title', 'Untitled')}\n"
            result += f"Description: {idea.get('description', 'No description')}\n"
            if 'related_concepts' in idea:
                result += "Related Concepts:\n"
                for concept in idea['related_concepts']:
                    result += f"- {concept}\n"
            result += "\n"
        return result

    def _format_schedule(self, schedule: Dict) -> str:
        """Format schedule for display"""
        if "error" in schedule:
            return f"Failed to optimize schedule: {schedule['error']}"
            
        result = "Optimized Schedule:\n\n"
        if 'tasks' in schedule:
            for task in schedule['tasks']:
                result += f"Task: {task.get('name')}\n"
                result += f"Start: {task.get('start_time')}\n"
                result += f"Duration: {task.get('duration')}\n"
                result += f"Priority: {task.get('priority')}\n\n"
        return result

    def _format_risks(self, risks: List[Dict]) -> str:
        """Format risk analysis for display"""
        if risks and "error" in risks[0]:
            return f"Failed to analyze risks: {risks[0]['error']}"
            
        result = "Risk Analysis:\n\n"
        for risk in risks:
            result += f"Risk: {risk.get('description', 'Unknown')}\n"
            result += f"Impact: {risk.get('impact', 'Unknown')}\n"
            result += f"Probability: {risk.get('probability', 'Unknown')}\n"
            if 'mitigation' in risk:
                result += "Mitigation Strategies:\n"
                for strategy in risk['mitigation']:
                    result += f"- {strategy}\n"
            result += "\n"
        return result

# Initialize the feature
project_manager_feature = ProjectManagerFeature()

# Export the command handler
async def handle_project_command(command: str) -> str:
    """Handle project management related voice commands"""
    return await project_manager_feature.process_command(command) 