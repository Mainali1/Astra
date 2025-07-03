
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from astra.core.database import database_manager, Script
from astra.home_edition.features.automation_manager import run_script_securely

def create_script(user_id: int, name: str, content: str, interpreter: str = 'python') -> Script:
    """
    Creates a new script for a specific user.

    Args:
        user_id: The ID of the user.
        name: The name of the script.
        content: The content of the script.
        interpreter: The interpreter to use for the script (e.g., 'python', 'bash').

    Returns:
        The created Script object.
    """
    with database_manager.get_session() as session:
        script = Script(
            user_id=user_id,
            name=name,
            content=content,
            interpreter=interpreter
        )
        session.add(script)
        session.commit()
        session.refresh(script)
        return script

def get_script(user_id: int, script_id: int) -> Optional[Script]:
    """
    Gets a specific script for a user.

    Args:
        user_id: The ID of the user.
        script_id: The ID of the script.

    Returns:
        The Script object if found, None otherwise.
    """
    with database_manager.get_session() as session:
        return session.query(Script).filter(
            Script.id == script_id,
            Script.user_id == user_id
        ).first()

def get_all_scripts(user_id: int) -> List[Script]:
    """
    Gets all scripts for a specific user.

    Args:
        user_id: The ID of the user.

    Returns:
        A list of Script objects.
    """
    with database_manager.get_session() as session:
        return session.query(Script).filter(Script.user_id == user_id).all()

def update_script(user_id: int, script_id: int, name: Optional[str] = None, content: Optional[str] = None, interpreter: Optional[str] = None) -> Optional[Script]:
    """
    Updates an existing script for a specific user.

    Args:
        user_id: The ID of the user.
        script_id: The ID of the script to update.
        name: The new name for the script (optional).
        content: The new content for the script (optional).
        interpreter: The new interpreter for the script (optional).

    Returns:
        The updated Script object if found, None otherwise.
    """
    with database_manager.get_session() as session:
        script = session.query(Script).filter(
            Script.id == script_id,
            Script.user_id == user_id
        ).first()
        if script:
            if name is not None:
                script.name = name
            if content is not None:
                script.content = content
            if interpreter is not None:
                script.interpreter = interpreter
            session.commit()
            session.refresh(script)
            return script
        return None

def delete_script(user_id: int, script_id: int) -> bool:
    """
    Deletes a script for a specific user.

    Args:
        user_id: The ID of the user.
        script_id: The ID of the script to delete.

    Returns:
        True if the script was deleted, False otherwise.
    """
    with database_manager.get_session() as session:
        script = session.query(Script).filter(
            Script.id == script_id,
            Script.user_id == user_id
        ).first()
        if script:
            session.delete(script)
            session.commit()
            return True
        return False

def execute_script(user_id: int, script_id: int) -> dict:
    """
    Executes a script for a specific user.

    Args:
        user_id: The ID of the user.
        script_id: The ID of the script to execute.

    Returns:
        A dictionary containing the execution status, stdout, stderr, and any error message.
    """
    with database_manager.get_session() as session:
        script = session.query(Script).filter(
            Script.id == script_id,
            Script.user_id == user_id
        ).first()
        if script:
            # Create a temporary file to execute the script
            temp_script_path = f"./temp_script_{script.id}.{script.interpreter}"
            with open(temp_script_path, 'w') as f:
                f.write(script.content)
            
            result = run_script_securely(temp_script_path, script.interpreter)
            
            # Clean up the temporary file
            import os
            os.remove(temp_script_path)
            
            return result
        return {"status": "error", "message": "Script not found."}
