"""
Script to build separate installers for Astra Home and Enterprise editions using Inno Setup.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List
from installer_config import AstraEdition, InstallerConfig

class AstraInstaller:
    def __init__(self, edition: AstraEdition):
        self.edition = edition
        self.build_dir = Path("build") / edition.value
        self.dist_dir = Path("dist") / edition.value
        self.version = "1.0.0"  # Read from version file or git tag
        
    def prepare_build_directory(self):
        """Prepare the build directory with only the files needed for this edition."""
        # Clean previous builds
        shutil.rmtree(self.build_dir, ignore_errors=True)
        shutil.rmtree(self.dist_dir, ignore_errors=True)
        
        # Create fresh directories
        self.build_dir.mkdir(parents=True)
        self.dist_dir.mkdir(parents=True)
        
        # Copy all files except those in exclude patterns
        exclude_patterns = InstallerConfig.get_exclude_patterns(self.edition)
        
        def should_copy(file_path: str) -> bool:
            return not any(Path(file_path).match(pattern) for pattern in exclude_patterns)
        
        # Copy source files
        for root, dirs, files in os.walk("src"):
            for file in files:
                src_path = Path(root) / file
                if should_copy(str(src_path)):
                    rel_path = src_path.relative_to("src")
                    dst_path = self.build_dir / "src" / rel_path
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
        
        # Copy core files
        core_files = ["main.py", "requirements.txt", "LICENSE.md", "README.md"]
        for file in core_files:
            if Path(file).exists():
                shutil.copy2(file, self.build_dir)
        
        # Create edition-specific requirements.txt
        self._create_requirements_file()
        
    def _create_requirements_file(self):
        """Create edition-specific requirements.txt with only needed dependencies."""
        deps = InstallerConfig.get_dependencies(self.edition)
        with open(self.build_dir / "requirements.txt", "w") as f:
            f.write("\n".join(deps))
            
    def generate_inno_script(self) -> str:
        """Generate the Inno Setup script for this edition."""
        app_name = f"Astra {self.edition.value.title()} Edition"
        app_version = self.version
        output_dir = str(self.dist_dir.absolute())
        source_dir = str(self.build_dir.absolute())
        
        script = f'''#define MyAppName "{app_name}"
#define MyAppVersion "{app_version}"
#define MyAppPublisher "Astra AI"
#define MyAppURL "https://astra-ai.com"
#define MyAppExeName "astra.exe"

[Setup]
AppId={{{app_name}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DisableProgramGroupPage=yes
LicenseFile={source_dir}\\LICENSE.md
OutputDir={output_dir}
OutputBaseFilename=astra_{self.edition.value}_setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "{source_dir}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent
'''
        return script
        
    def build(self):
        """Build the installer for this edition."""
        print(f"Building {self.edition.value} edition installer...")
        
        # Prepare build directory
        self.prepare_build_directory()
        
        # Generate Inno Setup script
        script = self.generate_inno_script()
        script_path = self.build_dir / f"astra_{self.edition.value}.iss"
        with open(script_path, "w") as f:
            f.write(script)
        
        # Run Inno Setup Compiler
        try:
            subprocess.run(["iscc", str(script_path)], check=True)
            print(f"Successfully built {self.edition.value} edition installer")
            print(f"Installer location: {self.dist_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Error building {self.edition.value} edition installer: {e}")
        except FileNotFoundError:
            print("Error: Inno Setup Compiler (iscc) not found. Please install Inno Setup.")

def main():
    """Build installers for both editions."""
    # Build Home Edition
    home_installer = AstraInstaller(AstraEdition.HOME)
    home_installer.build()
    
    # Build Enterprise Edition
    enterprise_installer = AstraInstaller(AstraEdition.ENTERPRISE)
    enterprise_installer.build()

if __name__ == "__main__":
    main() 