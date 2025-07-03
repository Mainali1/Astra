from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from astra.core.database import database_manager, TodoTask

def add_task(user_id: int, title: str, due_date: Optional[datetime] = None) -> TodoTask:
    """
    Adds a task to the to-do list for a specific user.

    :param user_id: The ID of the user.
    :param title: The title of the task.
    :param due_date: The due date of the task.
    :return: The created task.
    """
    with database_manager.get_session() as session:
        task = TodoTask(user_id=user_id, title=title, due_date=due_date)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

def get_tasks(user_id: int, completed: Optional[bool] = None) -> List[TodoTask]:
    """
    Gets all tasks for a user, with an optional filter for completion status.

    :param user_id: The ID of the user.
    :param completed: Whether to filter by completed status.
    :return: A list of tasks.
    """
    with database_manager.get_session() as session:
        query = session.query(TodoTask).filter(TodoTask.user_id == user_id)
        if completed is not None:
            query = query.filter(TodoTask.completed == completed)
        return query.all()

def complete_task(user_id: int, task_id: int) -> Optional[TodoTask]:
    """
    Marks a task as complete.

    :param user_id: The ID of the user.
    :param task_id: The ID of the task to complete.
    :return: The updated task, or None if not found.
    """
    with database_manager.get_session() as session:
        task = session.query(TodoTask).filter(
            TodoTask.id == task_id,
            TodoTask.user_id == user_id
        ).first()
        if task:
            task.completed = True
            session.commit()
            session.refresh(task)
            return task
        return None

def delete_task(user_id: int, task_id: int) -> bool:
    """
    Deletes a task for a specific user.

    :param user_id: The ID of the user.
    :param task_id: The ID of the task to delete.
    :return: True if the task was deleted, False otherwise.
    """
    with database_manager.get_session() as session:
        task = session.query(TodoTask).filter(
            TodoTask.id == task_id,
            TodoTask.user_id == user_id
        ).first()
        if task:
            session.delete(task)
            session.commit()
            return True
        return False