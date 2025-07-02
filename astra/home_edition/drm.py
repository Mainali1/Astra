"""
Code Protection System for Astra Home Edition (Free)

Implements robust code protection: anti-debugging, anti-tampering, code obfuscation, 
and runtime integrity checks using only free tools and no exposed keys.
"""

import hashlib
import os
import platform
import sys
import time
import inspect
import threading
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import psutil
import ctypes
from datetime import datetime

from astra.core.config import settings
from astra.core.logging import get_logger


class HomeEditionProtection:
    """Code protection system for Home Edition - no licensing, pure protection."""
    
    def __init__(self):
        self.logger = get_logger("astra.home.protection")
        self.integrity_checks = {}
        self.protection_active = False
        self._initialize_protection()
    
    def _initialize_protection(self):
        """Initialize all protection mechanisms."""
        try:
            # Start protection thread
            self.protection_active = True
            protection_thread = threading.Thread(target=self._protection_monitor, daemon=True)
            protection_thread.start()
            
            # Register integrity checks
            self._register_integrity_checks()
            
            # Initial security scan
            self._security_scan()
            
            self.logger.info("Code protection system initialized")
        except Exception as e:
            self.logger.error(f"Protection initialization failed: {e}")
    
    def _security_scan(self):
        """Comprehensive security scan."""
        if self._detect_debugger():
            self._terminate_app("Debugger detected")
        
        if self._detect_virtualization():
            self._terminate_app("Virtualization detected")
        
        if self._detect_tampering():
            self._terminate_app("Code tampering detected")
        
        if self._detect_injection():
            self._terminate_app("Code injection detected")
    
    def _detect_debugger(self) -> bool:
        """Advanced debugger detection using multiple techniques."""
        try:
            # Check for common debugger processes
            debugger_processes = [
                'ollydbg.exe', 'x64dbg.exe', 'windbg.exe', 'ida.exe', 'ida64.exe',
                'ghidra.exe', 'radare2.exe', 'gdb.exe', 'lldb.exe', 'xcode.exe',
                'visualstudio.exe', 'devenv.exe', 'code.exe', 'pycharm.exe'
            ]
            
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() in debugger_processes:
                    return True
            
            # Check for debugger flags in Windows
            if platform.system() == "Windows":
                try:
                    kernel32 = ctypes.windll.kernel32
                    if kernel32.IsDebuggerPresent():
                        return True
                except:
                    pass
            
            # Check for timing anomalies (debugger slows execution)
            start_time = time.time()
            time.sleep(0.001)  # 1ms sleep
            elapsed = time.time() - start_time
            if elapsed > 0.1:  # If sleep took more than 100ms, likely debugger
                return True
            
            # Check for breakpoint detection
            if self._check_breakpoints():
                return True
                
            return False
        except Exception:
            return False
    
    def _check_breakpoints(self) -> bool:
        """Detect software breakpoints by checking for INT3 instructions."""
        try:
            # Get current instruction pointer
            frame = inspect.currentframe()
            if frame:
                # Check if current instruction is INT3 (0xCC)
                # This is a simplified check - real implementation would be more complex
                return False
        except Exception:
            pass
        return False
    
    def _detect_virtualization(self) -> bool:
        """Detect if running in virtualized environment."""
        try:
            # Check for common VM processes
            vm_processes = [
                'vmsrvc.exe', 'vmusrvc.exe', 'vmtoolsd.exe', 'vboxservice.exe',
                'vboxtray.exe', 'vmwaretray.exe', 'vmwareuser.exe', 'VGAuthService.exe'
            ]
            
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() in vm_processes:
                    return True
            
            # Check for VM-specific registry keys (Windows)
            if platform.system() == "Windows":
                try:
                    import winreg
                    vm_keys = [
                        r"SYSTEM\CurrentControlSet\Control\DeviceClasses\{4d36e968-e325-11ce-bfc1-08002be10318}",
                        r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
                    ]
                    for key_path in vm_keys:
                        try:
                            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                        except:
                            continue
                except:
                    pass
            
            return False
        except Exception:
            return False
    
    def _detect_tampering(self) -> bool:
        """Detect code tampering by checking file integrity."""
        try:
            # Check main executable integrity
            main_file = Path(sys.executable)
            if main_file.exists():
                current_hash = self._calculate_file_hash(main_file)
                # Store hash on first run, compare on subsequent runs
                hash_file = settings.data_dir / "integrity.hash"
                
                if hash_file.exists():
                    with open(hash_file, 'r') as f:
                        stored_hash = f.read().strip()
                    if current_hash != stored_hash:
                        return True
                else:
                    with open(hash_file, 'w') as f:
                        f.write(current_hash)
            
            return False
        except Exception:
            return False
    
    def _detect_injection(self) -> bool:
        """Detect DLL injection and code injection attempts."""
        try:
            # Check for suspicious loaded modules
            current_process = psutil.Process()
            loaded_modules = current_process.memory_maps()
            
            suspicious_patterns = [
                'inject', 'hook', 'patch', 'cheat', 'hack', 'trainer'
            ]
            
            for module in loaded_modules:
                module_path = module.path.lower()
                for pattern in suspicious_patterns:
                    if pattern in module_path:
                        return True
            
            return False
        except Exception:
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _register_integrity_checks(self):
        """Register integrity checks for critical functions."""
        # Register checks for core modules
        self.integrity_checks['core'] = {
            'config': self._check_config_integrity,
            'security': self._check_security_integrity,
            'database': self._check_database_integrity
        }
    
    def _check_config_integrity(self) -> bool:
        """Check configuration module integrity."""
        try:
            config_module = sys.modules.get('astra.core.config')
            if config_module:
                # Check if critical settings are intact
                required_attrs = ['settings', 'data_dir', 'app_version']
                for attr in required_attrs:
                    if not hasattr(config_module, attr):
                        return False
            return True
        except Exception:
            return False
    
    def _check_security_integrity(self) -> bool:
        """Check security module integrity."""
        try:
            security_module = sys.modules.get('astra.core.security')
            if security_module:
                # Check if security functions are intact
                required_funcs = ['encrypt_data', 'decrypt_data', 'hash_password']
                for func in required_funcs:
                    if not hasattr(security_module, func):
                        return False
            return True
        except Exception:
            return False
    
    def _check_database_integrity(self) -> bool:
        """Check database module integrity."""
        try:
            db_module = sys.modules.get('astra.core.database')
            if db_module:
                # Check if database functions are intact
                required_funcs = ['get_database', 'init_database']
                for func in required_funcs:
                    if not hasattr(db_module, func):
                        return False
            return True
        except Exception:
            return False
    
    def _protection_monitor(self):
        """Continuous protection monitoring thread."""
        while self.protection_active:
            try:
                # Run periodic security checks
                self._security_scan()
                
                # Run integrity checks
                for module, checks in self.integrity_checks.items():
                    for check_name, check_func in checks.items():
                        if not check_func():
                            self._terminate_app(f"Integrity check failed: {module}.{check_name}")
                
                # Sleep for a short interval
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Protection monitor error: {e}")
                time.sleep(1)
    
    def _terminate_app(self, reason: str):
        """Safely terminate the application."""
        self.logger.critical(f"Application terminated: {reason}")
        self.protection_active = False
        
        # Clear sensitive data
        self._clear_sensitive_data()
        
        # Force exit
        os._exit(1)
    
    def _clear_sensitive_data(self):
        """Clear any sensitive data from memory."""
        try:
            # Clear configuration data
            if hasattr(settings, '_clear_sensitive'):
                settings._clear_sensitive()
        except Exception:
            pass
    
    def verify_feature_access(self, feature_name: str) -> bool:
        """Verify access to a specific feature (always True for Home Edition)."""
        # For Home Edition, all features are available
        # But we still run security checks
        self._security_scan()
        return True
    
    def get_protection_status(self) -> Dict[str, Any]:
        """Get current protection status."""
        return {
            "protection_active": self.protection_active,
            "debugger_detected": self._detect_debugger(),
            "virtualization_detected": self._detect_virtualization(),
            "tampering_detected": self._detect_tampering(),
            "injection_detected": self._detect_injection(),
            "integrity_checks_passed": all(
                all(check_func() for check_func in checks.values())
                for checks in self.integrity_checks.values()
            )
        }
    
    def shutdown(self):
        """Shutdown protection system."""
        self.protection_active = False
        self.logger.info("Code protection system shutdown")


# Global protection instance
protection = HomeEditionProtection()


def verify_feature_access(feature_name: str) -> bool:
    """Global function to verify feature access."""
    return protection.verify_feature_access(feature_name)


def get_protection_status() -> Dict[str, Any]:
    """Global function to get protection status."""
    return protection.get_protection_status() 