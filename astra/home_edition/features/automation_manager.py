import subprocess
import os
import logging

# Configure logging for the automation manager
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def run_script_securely(script_path: str, interpreter: str = 'python', timeout: int = 60) -> dict:
    """
    Executes a script securely with a timeout and captures its output.

    Args:
        script_path: The absolute path to the script to run.
        interpreter: The interpreter to use (e.g., 'python', 'bash').
        timeout: Maximum time in seconds to wait for the script to complete.

    Returns:
        A dictionary containing the execution status, stdout, stderr, and any error message.
    """
    if not os.path.isabs(script_path):
        return {"status": "error", "message": "Error: Script path must be absolute.", "stdout": "", "stderr": ""}

    if not os.path.exists(script_path):
        return {"status": "error", "message": f"Error: Script not found at {script_path}", "stdout": "", "stderr": ""}

    command = [interpreter, script_path]
    try:
        logger.info(f"Executing script: {' '.join(command)}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,  # Raise CalledProcessError for non-zero exit codes
            timeout=timeout
        )
        logger.info(f"Script executed successfully: {script_path}")
        return {"status": "success", "message": "Script executed successfully.", "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        logger.error(f"Script execution failed with non-zero exit code: {script_path}", exc_info=True)
        return {"status": "error", "message": f"Script exited with error code {e.returncode}.", "stdout": e.stdout, "stderr": e.stderr}
    except subprocess.TimeoutExpired:
        logger.warning(f"Script execution timed out: {script_path}")
        return {"status": "timeout", "message": f"Script timed out after {timeout} seconds.", "stdout": "", "stderr": ""}
    except FileNotFoundError:
        logger.error(f"Interpreter not found: {interpreter}", exc_info=True)
        return {"status": "error", "message": f"Error: Interpreter '{interpreter}' not found. Ensure it's in your PATH.", "stdout": "", "stderr": ""}
    except Exception as e:
        logger.error(f"An unexpected error occurred during script execution: {script_path}", exc_info=True)
        return {"status": "error", "message": f"An unexpected error occurred: {e}", "stdout": "", "stderr": ""}