"""
File Manager Feature for Astra Voice Assistant

This module provides file management capabilities including:
- List files and directories
- Search for files
- Get file information
- Create directories
- Delete files
- Voice commands for file operations
"""

import os
import shutil
import glob
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re


class FileInfo:
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.is_dir = os.path.isdir(path)
        self.size = self._get_size()
        self.modified = self._get_modified_time()
        self.extension = self._get_extension()
    
    def _get_size(self) -> Optional[int]:
        """Get file size in bytes"""
        try:
            if self.is_dir:
                return None
            return os.path.getsize(self.path)
        except:
            return None
    
    def _get_modified_time(self) -> Optional[datetime]:
        """Get last modified time"""
        try:
            timestamp = os.path.getmtime(self.path)
            return datetime.fromtimestamp(timestamp)
        except:
            return None
    
    def _get_extension(self) -> str:
        """Get file extension"""
        if self.is_dir:
            return ""
        return os.path.splitext(self.name)[1].lower()
    
    def get_formatted_size(self) -> str:
        """Get formatted file size"""
        if self.size is None:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024.0:
                return f"{self.size:.1f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.1f} TB"
    
    def get_formatted_date(self) -> str:
        """Get formatted modification date"""
        if self.modified is None:
            return "Unknown"
        return self.modified.strftime("%Y-%m-%d %H:%M")


class FileManager:
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.expanduser("~")
        self.current_path = self.base_path
    
    def get_current_directory(self) -> str:
        """Get current working directory"""
        return self.current_path
    
    def change_directory(self, path: str = "") -> bool:
        """Change to a different directory"""
        path = path or ""
        try:
            if os.path.isabs(path):
                new_path = path
            else:
                new_path = os.path.join(self.current_path, path)
            
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_path = os.path.abspath(new_path)
                return True
            return False
        except:
            return False
    
    def list_directory(self, path: str = "", show_hidden: bool = False) -> List[FileInfo]:
        """List contents of a directory"""
        path = path or ""
        try:
            target_path = path or self.current_path
            
            if not os.path.exists(target_path):
                return []
            
            items = []
            for item in os.listdir(target_path):
                if not show_hidden and item.startswith('.'):
                    continue
                
                item_path = os.path.join(target_path, item)
                items.append(FileInfo(item_path))
            
            # Sort: directories first, then files, both alphabetically
            items.sort(key=lambda x: (not x.is_dir, x.name.lower()))
            return items
            
        except Exception as e:
            print(f"Error listing directory: {e}")
            return []
    
    def search_files(self, query: str, path: str = "", recursive: bool = True) -> List[FileInfo]:
        """Search for files by name"""
        path = path or ""
        try:
            target_path = path or self.current_path
            results = []
            
            if recursive:
                # Use glob for recursive search
                pattern = os.path.join(target_path, "**", f"*{query}*")
                for file_path in glob.glob(pattern, recursive=True):
                    if os.path.isfile(file_path):
                        results.append(FileInfo(file_path))
            else:
                # Search only in current directory
                items = self.list_directory(target_path)
                for item in items:
                    if query.lower() in item.name.lower():
                        results.append(item)
            
            return results
            
        except Exception as e:
            print(f"Error searching files: {e}")
            return []
    
    def get_file_info(self, path: str = "") -> Optional[FileInfo]:
        """Get detailed information about a file"""
        path = path or ""
        try:
            if not os.path.isabs(path):
                path = os.path.join(self.current_path, path)
            
            if os.path.exists(path):
                return FileInfo(path)
            return None
            
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def create_directory(self, name: str = "") -> bool:
        """Create a new directory"""
        name = name or ""
        try:
            dir_path = os.path.join(self.current_path, name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                return True
            return False
            
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False
    
    def delete_file(self, path: str = "") -> bool:
        """Delete a file or directory"""
        path = path or ""
        try:
            if not os.path.isabs(path):
                path = os.path.join(self.current_path, path)
            
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def copy_file(self, source: str = "", destination: str = "") -> bool:
        """Copy a file"""
        source = source or ""
        destination = destination or ""
        try:
            if not os.path.isabs(source):
                source = os.path.join(self.current_path, source)
            if not os.path.isabs(destination):
                destination = os.path.join(self.current_path, destination)
            
            if os.path.exists(source):
                shutil.copy2(source, destination)
                return True
            return False
            
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
    
    def move_file(self, source: str = "", destination: str = "") -> bool:
        """Move a file"""
        source = source or ""
        destination = destination or ""
        try:
            if not os.path.isabs(source):
                source = os.path.join(self.current_path, source)
            if not os.path.isabs(destination):
                destination = os.path.join(self.current_path, destination)
            
            if os.path.exists(source):
                shutil.move(source, destination)
                return True
            return False
            
        except Exception as e:
            print(f"Error moving file: {e}")
            return False
    
    def get_disk_usage(self, path: str = None) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            target_path = path or self.current_path
            total, used, free = shutil.disk_usage(target_path)
            
            return {
                'total': total,
                'used': used,
                'free': free,
                'percent_used': (used / total) * 100
            }
            
        except Exception as e:
            print(f"Error getting disk usage: {e}")
            return {}
    
    def get_directory_size(self, path: str = None) -> int:
        """Get total size of a directory"""
        try:
            target_path = path or self.current_path
            total_size = 0
            
            for dirpath, dirnames, filenames in os.walk(target_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except:
                        continue
            
            return total_size
            
        except Exception as e:
            print(f"Error getting directory size: {e}")
            return 0


class FileManagerFeature:
    def __init__(self):
        self.file_manager = FileManager()
        self.navigation_history = []
    
    def process_command(self, command: str) -> str:
        """Process voice commands for file management"""
        command = command.lower().strip()
        
        # List directory contents
        if any(keyword in command for keyword in ["list files", "show files", "what's in", "contents of"]):
            return self._list_directory_from_command(command)
        
        # Change directory
        elif any(keyword in command for keyword in ["go to", "open folder", "navigate to", "cd"]):
            return self._change_directory_from_command(command)
        
        # Search files
        elif any(keyword in command for keyword in ["find file", "search for", "look for file"]):
            return self._search_files_from_command(command)
        
        # Get file info
        elif any(keyword in command for keyword in ["file info", "information about", "details of"]):
            return self._get_file_info_from_command(command)
        
        # Create directory
        elif any(keyword in command for keyword in ["create folder", "make directory", "new folder"]):
            return self._create_directory_from_command(command)
        
        # Delete file
        elif any(keyword in command for keyword in ["delete file", "remove file", "delete folder"]):
            return self._delete_file_from_command(command)
        
        # Copy file
        elif any(keyword in command for keyword in ["copy file", "duplicate file"]):
            return self._copy_file_from_command(command)
        
        # Move file
        elif any(keyword in command for keyword in ["move file", "rename file"]):
            return self._move_file_from_command(command)
        
        # Get current location
        elif any(keyword in command for keyword in ["where am i", "current folder", "current directory"]):
            return self._get_current_location()
        
        # Go back
        elif any(keyword in command for keyword in ["go back", "previous folder", "back"]):
            return self._go_back()
        
        # Disk usage
        elif any(keyword in command for keyword in ["disk usage", "storage info", "space used"]):
            return self._get_disk_usage()
        
        else:
            return ("I can help you manage files. Try saying:\n"
                   "• 'List files' or 'Show files'\n"
                   "• 'Go to [folder name]' or 'Open folder'\n"
                   "• 'Find file [name]' to search\n"
                   "• 'Create folder [name]' or 'Delete file [name]'")
    
    def _list_directory_from_command(self, command: str) -> str:
        """List directory contents from command"""
        # Check if specific directory mentioned
        items = self.file_manager.list_directory()
        
        if not items:
            return "This directory is empty."
        
        response = f"📁 Contents of {os.path.basename(self.file_manager.current_path)}:\n\n"
        
        # Group by type
        folders = [item for item in items if item.is_dir]
        files = [item for item in items if not item.is_dir]
        
        if folders:
            response += "📂 Folders:\n"
            for folder in folders[:10]:  # Limit to 10 folders
                response += f"   {folder.name}\n"
            if len(folders) > 10:
                response += f"   ... and {len(folders) - 10} more folders\n"
            response += "\n"
        
        if files:
            response += "📄 Files:\n"
            for file in files[:10]:  # Limit to 10 files
                size_str = file.get_formatted_size()
                response += f"   {file.name} ({size_str})\n"
            if len(files) > 10:
                response += f"   ... and {len(files) - 10} more files\n"
        
        return response
    
    def _change_directory_from_command(self, command: str) -> str:
        """Change directory from command"""
        # Extract directory name
        for keyword in ["go to", "open folder", "navigate to", "cd"]:
            command = command.replace(keyword, "").strip()
        
        if not command:
            return "Please specify a folder name."
        
        # Save current location for back navigation
        self.navigation_history.append(self.file_manager.current_path)
        
        if self.file_manager.change_directory(command):
            return f"📂 Changed to {os.path.basename(self.file_manager.current_path)}"
        else:
            return f"❌ Could not find folder '{command}'"
    
    def _search_files_from_command(self, command: str) -> str:
        """Search for files from command"""
        # Extract search query
        for keyword in ["find file", "search for", "look for file"]:
            command = command.replace(keyword, "").strip()
        
        if not command:
            return "Please specify a file name to search for."
        
        results = self.file_manager.search_files(command)
        
        if not results:
            return f"No files found matching '{command}'"
        
        response = f"🔍 Found {len(results)} files matching '{command}':\n\n"
        
        for i, file_info in enumerate(results[:10], 1):  # Limit to 10 results
            folder_emoji = "📂" if file_info.is_dir else "📄"
            size_str = file_info.get_formatted_size() if not file_info.is_dir else ""
            response += f"{i}. {folder_emoji} {file_info.name}"
            if size_str:
                response += f" ({size_str})"
            response += f"\n   📍 {file_info.path}\n\n"
        
        if len(results) > 10:
            response += f"... and {len(results) - 10} more results."
        
        return response
    
    def _get_file_info_from_command(self, command: str) -> str:
        """Get file information from command"""
        # Extract file name
        for keyword in ["file info", "information about", "details of"]:
            command = command.replace(keyword, "").strip()
        
        if not command:
            return "Please specify a file name."
        
        file_info = self.file_manager.get_file_info(command)
        
        if not file_info:
            return f"❌ File '{command}' not found"
        
        response = f"📋 Information about '{file_info.name}':\n\n"
        response += f"📁 Type: {'Folder' if file_info.is_dir else 'File'}\n"
        response += f"📏 Size: {file_info.get_formatted_size()}\n"
        response += f"📅 Modified: {file_info.get_formatted_date()}\n"
        response += f"📍 Path: {file_info.path}\n"
        
        if file_info.extension:
            response += f"📄 Extension: {file_info.extension}\n"
        
        return response
    
    def _create_directory_from_command(self, command: str) -> str:
        """Create directory from command"""
        # Extract directory name
        for keyword in ["create folder", "make directory", "new folder"]:
            command = command.replace(keyword, "").strip()
        
        if not command:
            return "Please specify a folder name."
        
        if self.file_manager.create_directory(command):
            return f"✅ Created folder '{command}'"
        else:
            return f"❌ Could not create folder '{command}' (may already exist)"
    
    def _delete_file_from_command(self, command: str) -> str:
        """Delete file from command"""
        # Extract file name
        for keyword in ["delete file", "remove file", "delete folder"]:
            command = command.replace(keyword, "").strip()
        
        if not command:
            return "Please specify a file or folder name."
        
        if self.file_manager.delete_file(command):
            return f"🗑️ Deleted '{command}'"
        else:
            return f"❌ Could not delete '{command}' (may not exist)"
    
    def _copy_file_from_command(self, command: str) -> str:
        """Copy file from command"""
        # This is a simplified version - in practice would need more parsing
        return "Copy functionality requires specifying source and destination. Please use the full command."
    
    def _move_file_from_command(self, command: str) -> str:
        """Move file from command"""
        # This is a simplified version - in practice would need more parsing
        return "Move functionality requires specifying source and destination. Please use the full command."
    
    def _get_current_location(self) -> str:
        """Get current directory location"""
        return f"📍 You are in: {self.file_manager.current_path}"
    
    def _go_back(self) -> str:
        """Go back to previous directory"""
        if not self.navigation_history:
            return "No previous location to go back to."
        
        previous_path = self.navigation_history.pop()
        self.file_manager.current_path = previous_path
        
        return f"⬅️ Went back to {os.path.basename(previous_path)}"
    
    def _get_disk_usage(self) -> str:
        """Get disk usage information"""
        usage = self.file_manager.get_disk_usage()
        
        if not usage:
            return "❌ Could not get disk usage information"
        
        total_gb = usage['total'] / (1024**3)
        used_gb = usage['used'] / (1024**3)
        free_gb = usage['free'] / (1024**3)
        
        response = f"💾 Disk Usage:\n\n"
        response += f"📊 Total: {total_gb:.1f} GB\n"
        response += f"📈 Used: {used_gb:.1f} GB ({usage['percent_used']:.1f}%)\n"
        response += f"📉 Free: {free_gb:.1f} GB\n"
        
        return response


# Global instance
file_manager_feature = FileManagerFeature()


def handle_file_manager_command(command: str, args: dict = None) -> dict:
    """Unified handler for file manager commands. Args: {action: ..., ...} """
    args = args or {}
    fm = FileManager()
    action = args.get('action')
    try:
        if action == 'list':
            path = args.get('path') or ''
            show_hidden = args.get('show_hidden', False)
            files = fm.list_directory(path, show_hidden)
            return {
                'success': True,
                'response': f'Listed {len(files)} items.',
                'data': [vars(f) for f in files]
            }
        elif action == 'search':
            query = args.get('query', '')
            path = args.get('path') or ''
            results = fm.search_files(query, path)
            return {
                'success': True,
                'response': f'Found {len(results)} files matching "{query}".',
                'data': [vars(f) for f in results]
            }
        elif action == 'info':
            path = args.get('path', '') or ''
            info = fm.get_file_info(path)
            if info:
                return {'success': True, 'response': 'File info retrieved.', 'data': vars(info)}
            else:
                return {'success': False, 'response': 'File not found.', 'error': 'Not found'}
        elif action == 'create_dir':
            name = args.get('name', '')
            ok = fm.create_directory(name)
            return {'success': ok, 'response': 'Directory created.' if ok else 'Failed to create directory.'}
        elif action == 'delete':
            path = args.get('path', '') or ''
            # Path sanitization: prevent directory traversal
            if '..' in path or path.startswith('/') or path.startswith('\\'):
                return {'success': False, 'response': 'Invalid path.', 'error': 'Path traversal detected'}
            ok = fm.delete_file(path)
            return {'success': ok, 'response': 'Deleted.' if ok else 'Failed to delete.'}
        elif action == 'copy':
            src = args.get('source', '') or ''
            dst = args.get('destination', '') or ''
            ok = fm.copy_file(src, dst)
            return {'success': ok, 'response': 'Copied.' if ok else 'Failed to copy.'}
        elif action == 'move':
            src = args.get('source', '') or ''
            dst = args.get('destination', '') or ''
            ok = fm.move_file(src, dst)
            return {'success': ok, 'response': 'Moved.' if ok else 'Failed to move.'}
        else:
            return {'success': False, 'response': 'Unknown action.', 'error': 'Unknown action'}
    except Exception as e:
        return {'success': False, 'response': f'Error: {e}', 'error': str(e)}


if __name__ == "__main__":
    # Test the file manager feature
    feature = FileManagerFeature()
    
    # Test commands
    test_commands = [
        "list files",
        "where am i",
        "disk usage",
        "create folder test_folder"
    ]
    
    for cmd in test_commands:
        print(f"Command: {cmd}")
        print(f"Response: {feature.process_command(cmd)}")
        print("-" * 50) 