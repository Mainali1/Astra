import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional

def list_directory_contents(path: str) -> List[Dict[str, Any]]:
    """
    Lists the contents (files and directories) of a given path.

    Args:
        path: The absolute path to the directory.

    Returns:
        A list of dictionaries, each representing a file or directory with its details.
    """
    if not os.path.isabs(path):
        return [{"error": "Path must be absolute."}]
    if not os.path.isdir(path):
        return [{"error": "Path is not a directory or does not exist."}]

    contents = []
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                is_dir = os.path.isdir(item_path)
                size = os.path.getsize(item_path) if not is_dir else 0
                created_at = datetime.fromtimestamp(os.path.getctime(item_path)).isoformat()
                modified_at = datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat()
                contents.append({
                    "name": item,
                    "path": item_path,
                    "is_directory": is_dir,
                    "size": size, # in bytes
                    "created_at": created_at,
                    "modified_at": modified_at
                })
            except OSError as e:
                # Log permission errors or other issues with specific files/dirs
                print(f"Warning: Could not access {item_path} - {e}")
                contents.append({"name": item, "path": item_path, "error": str(e)})
    except OSError as e:
        return [{"error": f"Error listing directory {path}: {e}"}]
    return contents

def create_directory(path: str) -> Dict[str, Any]:
    """
    Creates a new directory.

    Args:
        path: The absolute path for the new directory.

    Returns:
        A dictionary indicating success or error.
    """
    if not os.path.isabs(path):
        return {"error": "Path must be absolute."}
    try:
        os.makedirs(path, exist_ok=True)
        return {"status": "success", "message": f"Directory {path} created successfully."}
    except OSError as e:
        return {"status": "error", "message": f"Error creating directory {path}: {e}"}

def delete_path(path: str) -> Dict[str, Any]:
    """
    Deletes a file or an empty directory.

    Args:
        path: The absolute path to the file or directory to delete.

    Returns:
        A dictionary indicating success or error.
    """
    if not os.path.isabs(path):
        return {"error": "Path must be absolute."}
    if not os.path.exists(path):
        return {"error": "Path does not exist."}

    try:
        if os.path.isfile(path):
            os.remove(path)
            return {"status": "success", "message": f"File {path} deleted successfully."}
        elif os.path.isdir(path):
            # Only remove if empty to prevent accidental data loss
            if not os.listdir(path):
                os.rmdir(path)
                return {"status": "success", "message": f"Empty directory {path} deleted successfully."}
            else:
                return {"status": "error", "message": f"Directory {path} is not empty. Use force_delete_directory to remove non-empty directories."}
    except OSError as e:
        return {"status": "error", "message": f"Error deleting {path}: {e}"}

def force_delete_directory(path: str) -> Dict[str, Any]:
    """
    Deletes a directory and all its contents recursively. Use with caution.

    Args:
        path: The absolute path to the directory to delete.

    Returns:
        A dictionary indicating success or error.
    """
    if not os.path.isabs(path):
        return {"error": "Path must be absolute."}
    if not os.path.isdir(path):
        return {"error": "Path is not a directory or does not exist."}

    try:
        shutil.rmtree(path)
        return {"status": "success", "message": f"Directory {path} and its contents deleted successfully."}
    except OSError as e:
        return {"status": "error", "message": f"Error force deleting directory {path}: {e}"}

def move_path(source_path: str, destination_path: str) -> Dict[str, Any]:
    """
    Moves a file or directory from source to destination.

    Args:
        source_path: The absolute path of the item to move.
        destination_path: The absolute path to the destination.

    Returns:
        A dictionary indicating success or error.
    """
    if not os.path.isabs(source_path) or not os.path.isabs(destination_path):
        return {"error": "Both paths must be absolute."}
    if not os.path.exists(source_path):
        return {"error": "Source path does not exist."}

    try:
        shutil.move(source_path, destination_path)
        return {"status": "success", "message": f"Moved {source_path} to {destination_path}."}
    except shutil.Error as e:
        return {"status": "error", "message": f"Error moving {source_path} to {destination_path}: {e}"}

def copy_path(source_path: str, destination_path: str) -> Dict[str, Any]:
    """
    Copies a file or directory from source to destination.

    Args:
        source_path: The absolute path of the item to copy.
        destination_path: The absolute path to the destination.

    Returns:
        A dictionary indicating success or error.
    """
    if not os.path.isabs(source_path) or not os.path.isabs(destination_path):
        return {"error": "Both paths must be absolute."}
    if not os.path.exists(source_path):
        return {"error": "Source path does not exist."}

    try:
        if os.path.isfile(source_path):
            shutil.copy2(source_path, destination_path)
        elif os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
        return {"status": "success", "message": f"Copied {source_path} to {destination_path}."}
    except shutil.Error as e:
        return {"status": "error", "message": f"Error copying {source_path} to {destination_path}: {e}"}