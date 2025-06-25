import os
import sys
import shutil
from PyInstaller.__main__ import run

def build_windows_exe():
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # PyInstaller configuration
    run([
        'main.py',  # Main script
        '--name=Astra',  # Executable name
        '--onedir',  # Create a directory with all dependencies
        '--noconsole',  # No console window
        '--icon=assets/astra.ico',  # App icon
        '--add-data=Voice;Voice',  # Include voice models
        '--add-data=src;src',  # Include source code
        '--add-data=config;config',  # Include config files
        '--hidden-import=deepseek_client',
        '--hidden-import=uvicorn',
        '--hidden-import=fastapi',
        '--hidden-import=websockets',
        '--hidden-import=pydantic',
        '--clean',  # Clean PyInstaller cache
        '--noconfirm',  # No confirmation
    ])
    
    print("Build completed! Executable is in the dist/Astra directory.")

if __name__ == "__main__":
    build_windows_exe() 