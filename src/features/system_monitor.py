"""
Astra AI Assistant - System Monitor Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from src.config import Config

logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring functionality."""
    
    def __init__(self, config: Config):
        """Initialize system monitor."""
        self.config = config
        self.history_file = Path(config.DATA_DIR) / 'system_history.json'
        self.history: List[Dict[str, Any]] = []
        self.max_history = 1440  # Store 24 hours of data at 1-minute intervals
        self._load_history()
    
    def _load_history(self):
        """Load monitoring history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
                logger.info(f"Loaded {len(self.history)} history records")
        except Exception as e:
            logger.error(f"Error loading history: {str(e)}")
    
    def _save_history(self):
        """Save monitoring history to file."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump(self.history[-self.max_history:], f)
        except Exception as e:
            logger.error(f"Error saving history: {str(e)}")
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        cpu_freq = psutil.cpu_freq()
        return {
            'usage_percent': psutil.cpu_percent(interval=1),
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_total': psutil.cpu_count(logical=True),
            'frequency_current': cpu_freq.current if cpu_freq else 0,
            'frequency_min': cpu_freq.min if cpu_freq else 0,
            'frequency_max': cpu_freq.max if cpu_freq else 0
        }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'free': mem.free,
            'percent': mem.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_free': swap.free,
            'swap_percent': swap.percent
        }
    
    def get_disk_info(self) -> List[Dict[str, Any]]:
        """Get disk information."""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'filesystem': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except Exception:
                continue
        return disks
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information."""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'connections': len(psutil.net_connections())
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information."""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'hostname': platform.node(),
            'uptime': str(datetime.now() - boot_time),
            'boot_time': boot_time.isoformat(),
            'python_version': platform.python_version()
        }
    
    def update_history(self):
        """Update monitoring history."""
        current = {
            'timestamp': datetime.now().isoformat(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'network': self.get_network_info()
        }
        self.history.append(current)
        
        # Trim history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        self._save_history()
    
    def format_bytes(self, bytes: int) -> str:
        """Format bytes into human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} PB"

class SystemMonitorFeature:
    """System monitor feature for Astra."""
    
    def __init__(self, config: Config):
        """Initialize the system monitor feature."""
        self.config = config
        self.monitor = SystemMonitor(config)
    
    def _format_cpu_info(self, info: Dict[str, Any]) -> str:
        """Format CPU information."""
        return (
            f"CPU Usage: {info['usage_percent']}%\n"
            f"Cores: {info['cores_physical']} physical, {info['cores_total']} logical\n"
            f"Frequency: {info['frequency_current']:.1f} MHz "
            f"(Range: {info['frequency_min']:.1f} - {info['frequency_max']:.1f} MHz)"
        )
    
    def _format_memory_info(self, info: Dict[str, Any]) -> str:
        """Format memory information."""
        return (
            f"Memory Usage: {info['percent']}%\n"
            f"Total: {self.monitor.format_bytes(info['total'])}\n"
            f"Used: {self.monitor.format_bytes(info['used'])}\n"
            f"Available: {self.monitor.format_bytes(info['available'])}\n"
            f"Swap: {info['swap_percent']}% used "
            f"({self.monitor.format_bytes(info['swap_used'])} of {self.monitor.format_bytes(info['swap_total'])})"
        )
    
    def _format_disk_info(self, disks: List[Dict[str, Any]]) -> str:
        """Format disk information."""
        result = "Disk Usage:\n"
        for disk in disks:
            result += (
                f"\n{disk['mountpoint']} ({disk['filesystem']}):\n"
                f"  {disk['percent']}% used\n"
                f"  Total: {self.monitor.format_bytes(disk['total'])}\n"
                f"  Used: {self.monitor.format_bytes(disk['used'])}\n"
                f"  Free: {self.monitor.format_bytes(disk['free'])}"
            )
        return result
    
    def _format_network_info(self, info: Dict[str, Any]) -> str:
        """Format network information."""
        return (
            f"Network Statistics:\n"
            f"Sent: {self.monitor.format_bytes(info['bytes_sent'])}\n"
            f"Received: {self.monitor.format_bytes(info['bytes_recv'])}\n"
            f"Packets Sent: {info['packets_sent']}\n"
            f"Packets Received: {info['packets_recv']}\n"
            f"Active Connections: {info['connections']}"
        )
    
    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle system monitor-related intents."""
        try:
            action = intent.get('action', '')
            params = intent.get('parameters', {})
            
            # Update history on each request
            self.monitor.update_history()
            
            if action == 'get_system_status':
                # Get complete system status
                cpu_info = self.monitor.get_cpu_info()
                memory_info = self.monitor.get_memory_info()
                disk_info = self.monitor.get_disk_info()
                network_info = self.monitor.get_network_info()
                
                return (
                    "System Status:\n\n"
                    f"{self._format_cpu_info(cpu_info)}\n\n"
                    f"{self._format_memory_info(memory_info)}\n\n"
                    f"{self._format_disk_info(disk_info)}\n\n"
                    f"{self._format_network_info(network_info)}"
                )
                
            elif action == 'get_cpu_status':
                # Get CPU status only
                return self._format_cpu_info(self.monitor.get_cpu_info())
                
            elif action == 'get_memory_status':
                # Get memory status only
                return self._format_memory_info(self.monitor.get_memory_info())
                
            elif action == 'get_disk_status':
                # Get disk status only
                return self._format_disk_info(self.monitor.get_disk_info())
                
            elif action == 'get_network_status':
                # Get network status only
                return self._format_network_info(self.monitor.get_network_info())
                
            else:
                return "I'm not sure what system information you need."
            
        except Exception as e:
            logger.error(f"Error handling system monitor request: {str(e)}")
            return "I'm sorry, but I encountered an error monitoring the system."
    
    def is_available(self) -> bool:
        """Check if the feature is available."""
        return True  # System monitoring is always available
    
    async def cleanup(self):
        """Clean up resources."""
        pass  # No cleanup needed 