"""
Todo/Task Management Feature for Astra Voice Assistant

This module provides comprehensive task management capabilities including:
- Create, read, update, delete tasks
- Task categories and priorities
- Due date management
- Task completion tracking
- Search and filtering
- Voice commands for task management
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    category: str = "general"
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[str] = None
    created_at: str = ""
    completed_at: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class TodoManager:
    def __init__(self, storage_file: str = "tasks.json"):
        self.storage_file = storage_file
        self.tasks: Dict[str, Task] = {}
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = {
                        task_id: Task(**task_data) 
                        for task_id, task_data in data.items()
                    }
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = {}
    
    def save_tasks(self):
        """Save tasks to storage file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {task_id: asdict(task) for task_id, task in self.tasks.items()},
                    f, indent=2, ensure_ascii=False
                )
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def create_task(self, title: str, description: str = "", category: str = "general",
                   priority: Priority = Priority.MEDIUM, due_date: Optional[str] = None,
                   tags: List[str] = None) -> str:
        """Create a new task"""
        task_id = f"task_{len(self.tasks) + 1}_{int(datetime.now().timestamp())}"
        task = Task(
            id=task_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            due_date=due_date,
            tags=tags or []
        )
        self.tasks[task_id] = task
        self.save_tasks()
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a specific task by ID"""
        return self.tasks.get(task_id)
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update a task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        self.save_tasks()
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save_tasks()
            return True
        return False
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            self.save_tasks()
            return True
        return False
    
    def get_tasks(self, status: Optional[TaskStatus] = None, 
                  category: Optional[str] = None, 
                  priority: Optional[Priority] = None) -> List[Task]:
        """Get filtered tasks"""
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        if category:
            tasks = [t for t in tasks if t.category.lower() == category.lower()]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        
        return sorted(tasks, key=lambda x: x.created_at, reverse=True)
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get tasks that are overdue"""
        now = datetime.now()
        overdue = []
        
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and 
                task.due_date and 
                datetime.fromisoformat(task.due_date) < now):
                overdue.append(task)
        
        return sorted(overdue, key=lambda x: x.due_date)
    
    def get_due_soon_tasks(self, days: int = 3) -> List[Task]:
        """Get tasks due within specified days"""
        now = datetime.now()
        due_soon = []
        
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and 
                task.due_date):
                due_date = datetime.fromisoformat(task.due_date)
                if now <= due_date <= now + timedelta(days=days):
                    due_soon.append(task)
        
        return sorted(due_soon, key=lambda x: x.due_date)
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title, description, or tags"""
        query = query.lower()
        results = []
        
        for task in self.tasks.values():
            if (query in task.title.lower() or 
                query in task.description.lower() or
                any(query in tag.lower() for tag in task.tags)):
                results.append(task)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        total = len(self.tasks)
        completed = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        pending = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        overdue = len(self.get_overdue_tasks())
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }


class TodoFeature:
    def __init__(self):
        self.todo_manager = TodoManager()
        self.priority_keywords = {
            "low": Priority.LOW,
            "medium": Priority.MEDIUM,
            "high": Priority.HIGH,
            "urgent": Priority.URGENT,
            "critical": Priority.URGENT
        }
    
    def process_command(self, command: str) -> str:
        """Process voice commands for todo management"""
        command = command.lower().strip()
        
        # Create task patterns
        if any(keyword in command for keyword in ["add task", "create task", "new task", "add todo"]):
            return self._create_task_from_command(command)
        
        # List tasks patterns
        elif any(keyword in command for keyword in ["list tasks", "show tasks", "my tasks", "view tasks"]):
            return self._list_tasks_from_command(command)
        
        # Complete task patterns
        elif any(keyword in command for keyword in ["complete task", "finish task", "mark done", "task done"]):
            return self._complete_task_from_command(command)
        
        # Delete task patterns
        elif any(keyword in command for keyword in ["delete task", "remove task", "cancel task"]):
            return self._delete_task_from_command(command)
        
        # Search tasks
        elif "search" in command and "task" in command:
            return self._search_tasks_from_command(command)
        
        # Get statistics
        elif any(keyword in command for keyword in ["task stats", "todo stats", "task summary"]):
            return self._get_statistics()
        
        # Get overdue tasks
        elif "overdue" in command:
            return self._get_overdue_tasks()
        
        # Get due soon tasks
        elif any(keyword in command for keyword in ["due soon", "upcoming", "due today"]):
            return self._get_due_soon_tasks()
        
        else:
            return "I can help you manage tasks. Try saying 'add task', 'list tasks', 'complete task', or 'task stats'."
    
    def _create_task_from_command(self, command: str) -> str:
        """Extract task details from voice command"""
        # Remove command keywords
        for keyword in ["add task", "create task", "new task", "add todo"]:
            command = command.replace(keyword, "").strip()
        
        # Extract priority
        priority = Priority.MEDIUM
        for keyword, pri in self.priority_keywords.items():
            if keyword in command:
                priority = pri
                command = command.replace(keyword, "").strip()
                break
        
        # Extract category (after "in" or "for")
        category = "general"
        if " in " in command:
            parts = command.split(" in ")
            if len(parts) > 1:
                category = parts[1].split()[0]
                command = parts[0]
        elif " for " in command:
            parts = command.split(" for ")
            if len(parts) > 1:
                category = parts[1].split()[0]
                command = parts[0]
        
        # Extract due date
        due_date = None
        date_patterns = [
            r"due (today|tomorrow|next week|next month)",
            r"by (today|tomorrow|next week|next month)",
            r"on (\d{1,2}/\d{1,2})",
            r"(\d{1,2}/\d{1,2})"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, command)
            if match:
                date_str = match.group(1)
                if date_str == "today":
                    due_date = datetime.now().date().isoformat()
                elif date_str == "tomorrow":
                    due_date = (datetime.now() + timedelta(days=1)).date().isoformat()
                elif date_str == "next week":
                    due_date = (datetime.now() + timedelta(days=7)).date().isoformat()
                elif date_str == "next month":
                    due_date = (datetime.now() + timedelta(days=30)).date().isoformat()
                else:
                    # Simple date format MM/DD
                    try:
                        month, day = map(int, date_str.split('/'))
                        year = datetime.now().year
                        due_date = datetime(year, month, day).date().isoformat()
                    except:
                        pass
                
                command = command.replace(match.group(0), "").strip()
                break
        
        # Clean up the title
        title = command.strip()
        if not title:
            return "Please provide a task title."
        
        # Create the task
        task_id = self.todo_manager.create_task(
            title=title,
            category=category,
            priority=priority,
            due_date=due_date
        )
        
        task = self.todo_manager.get_task(task_id)
        return f"Task created: '{task.title}' in {task.category} category with {task.priority.value} priority."
    
    def _list_tasks_from_command(self, command: str) -> str:
        """List tasks based on command filters"""
        tasks = self.todo_manager.get_tasks()
        
        if "completed" in command:
            tasks = self.todo_manager.get_tasks(status=TaskStatus.COMPLETED)
        elif "pending" in command:
            tasks = self.todo_manager.get_tasks(status=TaskStatus.PENDING)
        elif "overdue" in command:
            tasks = self.todo_manager.get_overdue_tasks()
        elif "due soon" in command:
            tasks = self.todo_manager.get_due_soon_tasks()
        
        if not tasks:
            return "No tasks found."
        
        response = f"Found {len(tasks)} tasks:\n"
        for i, task in enumerate(tasks[:10], 1):  # Limit to 10 tasks
            status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "⏳"
            priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "urgent": "🔴"}[task.priority.value]
            
            response += f"{i}. {status_emoji} {priority_emoji} {task.title}"
            if task.category != "general":
                response += f" ({task.category})"
            if task.due_date:
                response += f" - Due: {task.due_date}"
            response += "\n"
        
        if len(tasks) > 10:
            response += f"\n... and {len(tasks) - 10} more tasks."
        
        return response
    
    def _complete_task_from_command(self, command: str) -> str:
        """Complete a task by title"""
        # Remove command keywords
        for keyword in ["complete task", "finish task", "mark done", "task done"]:
            command = command.replace(keyword, "").strip()
        
        # Find task by title
        tasks = self.todo_manager.search_tasks(command)
        if not tasks:
            return f"No task found matching '{command}'."
        
        # Complete the first matching task
        task = tasks[0]
        if self.todo_manager.complete_task(task.id):
            return f"Task '{task.title}' marked as completed!"
        else:
            return "Failed to complete the task."
    
    def _delete_task_from_command(self, command: str) -> str:
        """Delete a task by title"""
        # Remove command keywords
        for keyword in ["delete task", "remove task", "cancel task"]:
            command = command.replace(keyword, "").strip()
        
        # Find task by title
        tasks = self.todo_manager.search_tasks(command)
        if not tasks:
            return f"No task found matching '{command}'."
        
        # Delete the first matching task
        task = tasks[0]
        if self.todo_manager.delete_task(task.id):
            return f"Task '{task.title}' has been deleted."
        else:
            return "Failed to delete the task."
    
    def _search_tasks_from_command(self, command: str) -> str:
        """Search tasks by query"""
        # Extract search query
        query = command.replace("search", "").replace("task", "").replace("tasks", "").strip()
        if not query:
            return "Please provide a search term."
        
        tasks = self.todo_manager.search_tasks(query)
        if not tasks:
            return f"No tasks found matching '{query}'."
        
        response = f"Found {len(tasks)} tasks matching '{query}':\n"
        for i, task in enumerate(tasks[:5], 1):  # Limit to 5 results
            status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "⏳"
            response += f"{i}. {status_emoji} {task.title} ({task.category})\n"
        
        if len(tasks) > 5:
            response += f"\n... and {len(tasks) - 5} more results."
        
        return response
    
    def _get_statistics(self) -> str:
        """Get task statistics"""
        stats = self.todo_manager.get_statistics()
        return (f"Task Statistics:\n"
                f"📊 Total tasks: {stats['total']}\n"
                f"✅ Completed: {stats['completed']}\n"
                f"⏳ Pending: {stats['pending']}\n"
                f"🔴 Overdue: {stats['overdue']}\n"
                f"📈 Completion rate: {stats['completion_rate']:.1f}%")
    
    def _get_overdue_tasks(self) -> str:
        """Get overdue tasks"""
        tasks = self.todo_manager.get_overdue_tasks()
        if not tasks:
            return "No overdue tasks! 🎉"
        
        response = f"You have {len(tasks)} overdue tasks:\n"
        for i, task in enumerate(tasks[:5], 1):
            response += f"{i}. 🔴 {task.title} - Due: {task.due_date}\n"
        
        if len(tasks) > 5:
            response += f"\n... and {len(tasks) - 5} more overdue tasks."
        
        return response
    
    def _get_due_soon_tasks(self) -> str:
        """Get tasks due soon"""
        tasks = self.todo_manager.get_due_soon_tasks()
        if not tasks:
            return "No tasks due soon."
        
        response = f"You have {len(tasks)} tasks due soon:\n"
        for i, task in enumerate(tasks[:5], 1):
            response += f"{i}. ⏰ {task.title} - Due: {task.due_date}\n"
        
        if len(tasks) > 5:
            response += f"\n... and {len(tasks) - 5} more tasks due soon."
        
        return response


# Global instance
todo_feature = TodoFeature()


def handle_todo_command(command: str) -> str:
    """Handle todo-related voice commands"""
    return todo_feature.process_command(command)


if __name__ == "__main__":
    # Test the todo feature
    feature = TodoFeature()
    
    # Test commands
    test_commands = [
        "add task buy groceries",
        "add task call mom high priority",
        "add task finish report in work due tomorrow",
        "list tasks",
        "list completed tasks",
        "complete task buy groceries",
        "search task report",
        "task stats"
    ]
    
    for cmd in test_commands:
        print(f"Command: {cmd}")
        print(f"Response: {feature.process_command(cmd)}")
        print("-" * 50) 