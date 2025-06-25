import os
import sys
import subprocess
import platform
from pathlib import Path

def build_windows():
    """Build Windows executable"""
    print("Building Windows executable...")
    try:
        # Run PyInstaller script
        subprocess.run([sys.executable, "scripts/build_windows.py"], check=True)
        print("Windows build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error building Windows executable: {e}")
        sys.exit(1)

def build_android():
    """Build Android APK"""
    print("Building Android APK...")
    try:
        # Change to Flutter client directory
        os.chdir("flutter_client")
        
        # Clean and get dependencies
        subprocess.run(["flutter", "clean"], check=True)
        subprocess.run(["flutter", "pub", "get"], check=True)
        
        # Build APK
        subprocess.run(["flutter", "build", "apk", "--release"], check=True)
        
        # Copy APK to dist directory
        dist_dir = Path("../dist")
        dist_dir.mkdir(exist_ok=True)
        
        apk_path = Path("build/app/outputs/flutter-apk/app-release.apk")
        if apk_path.exists():
            target_path = dist_dir / "Astra.apk"
            apk_path.rename(target_path)
            print(f"Android APK built successfully: {target_path}")
        else:
            print("Error: APK not found after build")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"Error building Android APK: {e}")
        sys.exit(1)
    finally:
        # Return to root directory
        os.chdir("..")

def main():
    # Create dist directory if it doesn't exist
    os.makedirs("dist", exist_ok=True)
    
    if len(sys.argv) > 1:
        platform_arg = sys.argv[1].lower()
        if platform_arg == "windows":
            build_windows()
        elif platform_arg == "android":
            build_android()
        else:
            print(f"Unknown platform: {platform_arg}")
            print("Usage: python scripts/build.py [windows|android]")
            sys.exit(1)
    else:
        # Build for current platform
        system = platform.system().lower()
        if system == "windows":
            build_windows()
        else:
            print("Please specify platform: python scripts/build.py [windows|android]")
            sys.exit(1)

if __name__ == "__main__":
    main() 