"""
System Monitor Feature for Astra Voice Assistant

This module provides system monitoring capabilities including:
- CPU usage and temperature
- Memory usage
- Disk usage and health
- Network status
- System information
- Voice commands for system monitoring
"""

import psutil
import platform
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess
import re


class SystemMonitor:
    def __init__(self):
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_version': platform.python_version()
        }
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information and usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Get CPU temperature (platform dependent)
            cpu_temp = self._get_cpu_temperature()
            
            return {
                'usage_percent': cpu_percent,
                'count': cpu_count,
                'frequency_mhz': cpu_freq.current if cpu_freq else None,
                'temperature_celsius': cpu_temp,
                'load_average': self._get_load_average()
            }
        except Exception as e:
            print(f"Error getting CPU info: {e}")
            return {}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information and usage"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent_used': memory.percent,
                'swap_total_gb': swap.total / (1024**3),
                'swap_used_gb': swap.used / (1024**3),
                'swap_percent_used': swap.percent
            }
        except Exception as e:
            print(f"Error getting memory info: {e}")
            return {}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk information and usage"""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            return {
                'total_gb': disk_usage.total / (1024**3),
                'used_gb': disk_usage.used / (1024**3),
                'free_gb': disk_usage.free / (1024**3),
                'percent_used': disk_usage.percent,
                'read_bytes_gb': disk_io.read_bytes / (1024**3) if disk_io else 0,
                'write_bytes_gb': disk_io.write_bytes / (1024**3) if disk_io else 0
            }
        except Exception as e:
            print(f"Error getting disk info: {e}")
            return {}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information and usage"""
        try:
            network_io = psutil.net_io_counters()
            network_interfaces = psutil.net_if_addrs()
            
            return {
                'bytes_sent_gb': network_io.bytes_sent / (1024**3),
                'bytes_recv_gb': network_io.bytes_recv / (1024**3),
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv,
                'interfaces': list(network_interfaces.keys())
            }
        except Exception as e:
            print(f"Error getting network info: {e}")
            return {}
    
    def get_process_info(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top processes by CPU and memory usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:limit]
            
        except Exception as e:
            print(f"Error getting process info: {e}")
            return []
    
    def get_battery_info(self) -> Optional[Dict[str, Any]]:
        """Get battery information (for laptops)"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'power_plugged': battery.power_plugged,
                    'time_left_minutes': battery.secsleft // 60 if battery.secsleft != -1 else None
                }
            return None
        except Exception as e:
            print(f"Error getting battery info: {e}")
            return None
    
    def get_system_uptime(self) -> float:
        """Get system uptime in seconds"""
        try:
            return time.time() - psutil.boot_time()
        except Exception as e:
            print(f"Error getting uptime: {e}")
            return 0
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature (platform dependent)"""
        try:
            if platform.system() == "Windows":
                # Windows - try using wmic
                result = subprocess.run(['wmic', 'cpu', 'get', 'temperature'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        temp_str = lines[1].strip()
                        if temp_str.isdigit():
                            return float(temp_str) / 10  # Convert from tenths of Kelvin
            
            elif platform.system() == "Linux":
                # Linux - try reading from thermal zone
                for i in range(10):
                    temp_file = f"/sys/class/thermal/thermal_zone{i}/temp"
                    if os.path.exists(temp_file):
                        with open(temp_file, 'r') as f:
                            temp = float(f.read().strip()) / 1000
                            return temp
            
            return None
            
        except Exception as e:
            print(f"Error getting CPU temperature: {e}")
            return None
    
    def _get_load_average(self) -> Optional[float]:
        """Get system load average"""
        try:
            if platform.system() == "Linux":
                with open('/proc/loadavg', 'r') as f:
                    load_avg = f.read().split()[0]
                    return float(load_avg)
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(['uptime'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse load average from uptime output
                    match = re.search(r'load average: ([\d.]+)', result.stdout)
                    if match:
                        return float(match.group(1))
            return None
            
        except Exception as e:
            print(f"Error getting load average: {e}")
            return None
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health assessment"""
        try:
            cpu_info = self.get_cpu_info()
            memory_info = self.get_memory_info()
            disk_info = self.get_disk_info()
            
            health_score = 100
            issues = []
            
            # Check CPU usage
            if cpu_info.get('usage_percent', 0) > 90:
                health_score -= 20
                issues.append("High CPU usage")
            elif cpu_info.get('usage_percent', 0) > 70:
                health_score -= 10
                issues.append("Elevated CPU usage")
            
            # Check memory usage
            if memory_info.get('percent_used', 0) > 90:
                health_score -= 20
                issues.append("High memory usage")
            elif memory_info.get('percent_used', 0) > 80:
                health_score -= 10
                issues.append("Elevated memory usage")
            
            # Check disk usage
            if disk_info.get('percent_used', 0) > 90:
                health_score -= 15
                issues.append("High disk usage")
            elif disk_info.get('percent_used', 0) > 80:
                health_score -= 5
                issues.append("Elevated disk usage")
            
            # Check CPU temperature
            if cpu_info.get('temperature_celsius'):
                temp = cpu_info['temperature_celsius']
                if temp > 85:
                    health_score -= 15
                    issues.append("High CPU temperature")
                elif temp > 70:
                    health_score -= 5
                    issues.append("Elevated CPU temperature")
            
            return {
                'score': max(0, health_score),
                'status': self._get_health_status(health_score),
                'issues': issues,
                'recommendations': self._get_health_recommendations(issues)
            }
            
        except Exception as e:
            print(f"Error getting system health: {e}")
            return {'score': 0, 'status': 'Unknown', 'issues': [], 'recommendations': []}
    
    def _get_health_status(self, score: int) -> str:
        """Get health status based on score"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Critical"
    
    def _get_health_recommendations(self, issues: List[str]) -> List[str]:
        """Get recommendations based on issues"""
        recommendations = []
        
        for issue in issues:
            if "CPU usage" in issue:
                recommendations.append("Close unnecessary applications to reduce CPU load")
            elif "memory usage" in issue:
                recommendations.append("Close applications or restart to free up memory")
            elif "disk usage" in issue:
                recommendations.append("Clean up disk space by removing unnecessary files")
            elif "temperature" in issue:
                recommendations.append("Check cooling system and clean dust from vents")
        
        return recommendations


class SystemMonitorFeature:
    def __init__(self):
        self.monitor = SystemMonitor()
    
    def process_command(self, command: str) -> str:
        """Process voice commands for system monitoring"""
        command = command.lower().strip()
        
        # CPU information
        if any(keyword in command for keyword in ["cpu usage", "processor usage", "cpu info"]):
            return self._get_cpu_status()
        
        # Memory information
        elif any(keyword in command for keyword in ["memory usage", "ram usage", "memory info"]):
            return self._get_memory_status()
        
        # Disk information
        elif any(keyword in command for keyword in ["disk usage", "storage usage", "disk info"]):
            return self._get_disk_status()
        
        # Network information
        elif any(keyword in command for keyword in ["network usage", "internet usage", "network info"]):
            return self._get_network_status()
        
        # System health
        elif any(keyword in command for keyword in ["system health", "computer health", "system status"]):
            return self._get_system_health()
        
        # Process information
        elif any(keyword in command for keyword in ["top processes", "running processes", "process list"]):
            return self._get_process_status()
        
        # Battery information
        elif any(keyword in command for keyword in ["battery status", "battery level", "power status"]):
            return self._get_battery_status()
        
        # System information
        elif any(keyword in command for keyword in ["system info", "computer info", "system details"]):
            return self._get_system_info()
        
        # Uptime
        elif any(keyword in command for keyword in ["uptime", "system uptime", "how long running"]):
            return self._get_uptime()
        
        # Full system report
        elif any(keyword in command for keyword in ["full report", "complete status", "system report"]):
            return self._get_full_system_report()
        
        else:
            return ("I can monitor your system. Try saying:\n"
                   "• 'CPU usage' or 'Memory usage'\n"
                   "• 'System health' for overall status\n"
                   "• 'Top processes' for running applications\n"
                   "• 'System info' for computer details")
    
    def _get_cpu_status(self) -> str:
        """Get CPU status"""
        cpu_info = self.monitor.get_cpu_info()
        
        if not cpu_info:
            return "❌ Could not get CPU information"
        
        response = f"🖥️ CPU Status:\n\n"
        response += f"📊 Usage: {cpu_info.get('usage_percent', 0):.1f}%\n"
        response += f"🔢 Cores: {cpu_info.get('count', 0)}\n"
        
        if cpu_info.get('frequency_mhz'):
            response += f"⚡ Frequency: {cpu_info.get('frequency_mhz', 0):.0f} MHz\n"
        
        if cpu_info.get('temperature_celsius'):
            temp = cpu_info['temperature_celsius']
            temp_emoji = "🔥" if temp > 70 else "🌡️"
            response += f"{temp_emoji} Temperature: {temp:.1f}°C\n"
        
        if cpu_info.get('load_average'):
            response += f"📈 Load Average: {cpu_info['load_average']:.2f}\n"
        
        return response
    
    def _get_memory_status(self) -> str:
        """Get memory status"""
        memory_info = self.monitor.get_memory_info()
        
        if not memory_info:
            return "❌ Could not get memory information"
        
        response = f"🧠 Memory Status:\n\n"
        response += f"📊 Usage: {memory_info.get('percent_used', 0):.1f}%\n"
        response += f"💾 Total: {memory_info.get('total_gb', 0):.1f} GB\n"
        response += f"📈 Used: {memory_info.get('used_gb', 0):.1f} GB\n"
        response += f"📉 Available: {memory_info.get('available_gb', 0):.1f} GB\n"
        
        if memory_info.get('swap_total_gb', 0) > 0:
            response += f"\n💿 Swap Usage: {memory_info.get('swap_percent_used', 0):.1f}%\n"
            response += f"💿 Swap Total: {memory_info.get('swap_total_gb', 0):.1f} GB\n"
        
        return response
    
    def _get_disk_status(self) -> str:
        """Get disk status"""
        disk_info = self.monitor.get_disk_info()
        
        if not disk_info:
            return "❌ Could not get disk information"
        
        response = f"💾 Disk Status:\n\n"
        response += f"📊 Usage: {disk_info.get('percent_used', 0):.1f}%\n"
        response += f"💾 Total: {disk_info.get('total_gb', 0):.1f} GB\n"
        response += f"📈 Used: {disk_info.get('used_gb', 0):.1f} GB\n"
        response += f"📉 Free: {disk_info.get('free_gb', 0):.1f} GB\n"
        
        if disk_info.get('read_bytes_gb', 0) > 0 or disk_info.get('write_bytes_gb', 0) > 0:
            response += f"\n📖 Read: {disk_info.get('read_bytes_gb', 0):.2f} GB\n"
            response += f"✏️ Written: {disk_info.get('write_bytes_gb', 0):.2f} GB\n"
        
        return response
    
    def _get_network_status(self) -> str:
        """Get network status"""
        network_info = self.monitor.get_network_info()
        
        if not network_info:
            return "❌ Could not get network information"
        
        response = f"🌐 Network Status:\n\n"
        response += f"📤 Sent: {network_info.get('bytes_sent_gb', 0):.2f} GB\n"
        response += f"📥 Received: {network_info.get('bytes_recv_gb', 0):.2f} GB\n"
        response += f"📦 Packets Sent: {network_info.get('packets_sent', 0):,}\n"
        response += f"📦 Packets Received: {network_info.get('packets_recv', 0):,}\n"
        
        if network_info.get('interfaces'):
            response += f"\n🔌 Interfaces: {', '.join(network_info['interfaces'][:5])}"
            if len(network_info['interfaces']) > 5:
                response += f" and {len(network_info['interfaces']) - 5} more"
        
        return response
    
    def _get_system_health(self) -> str:
        """Get system health assessment"""
        health = self.monitor.get_system_health()
        
        if not health:
            return "❌ Could not get system health information"
        
        status_emoji = {
            "Excellent": "🟢",
            "Good": "🟡",
            "Fair": "🟠",
            "Poor": "🔴",
            "Critical": "⚫"
        }.get(health['status'], "❓")
        
        response = f"{status_emoji} System Health: {health['status']} ({health['score']}/100)\n\n"
        
        if health['issues']:
            response += "⚠️ Issues Found:\n"
            for issue in health['issues']:
                response += f"   • {issue}\n"
            response += "\n"
        
        if health['recommendations']:
            response += "💡 Recommendations:\n"
            for rec in health['recommendations']:
                response += f"   • {rec}\n"
        
        return response
    
    def _get_process_status(self) -> str:
        """Get top processes"""
        processes = self.monitor.get_process_info(limit=8)
        
        if not processes:
            return "❌ Could not get process information"
        
        response = f"📋 Top Processes:\n\n"
        
        for i, proc in enumerate(processes, 1):
            response += f"{i}. {proc['name']}\n"
            response += f"   CPU: {proc['cpu_percent']:.1f}% | RAM: {proc['memory_percent']:.1f}%\n"
        
        return response
    
    def _get_battery_status(self) -> str:
        """Get battery status"""
        battery_info = self.monitor.get_battery_info()
        
        if not battery_info:
            return "🔌 No battery detected (desktop computer or battery not available)"
        
        battery_emoji = "🔋" if battery_info['power_plugged'] else "🔋"
        status = "Plugged In" if battery_info['power_plugged'] else "On Battery"
        
        response = f"{battery_emoji} Battery Status:\n\n"
        response += f"📊 Level: {battery_info['percent']}%\n"
        response += f"⚡ Status: {status}\n"
        
        if battery_info.get('time_left_minutes'):
            hours = battery_info['time_left_minutes'] // 60
            minutes = battery_info['time_left_minutes'] % 60
            response += f"⏰ Time Left: {hours}h {minutes}m\n"
        
        return response
    
    def _get_system_info(self) -> str:
        """Get system information"""
        info = self.monitor.system_info
        
        response = f"💻 System Information:\n\n"
        response += f"🖥️ OS: {info['platform']} {info['platform_version']}\n"
        response += f"🏗️ Architecture: {info['architecture']}\n"
        response += f"🔧 Processor: {info['processor']}\n"
        response += f"🏠 Hostname: {info['hostname']}\n"
        response += f"🐍 Python: {info['python_version']}\n"
        
        return response
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        uptime_seconds = self.monitor.get_system_uptime()
        
        if uptime_seconds == 0:
            return "❌ Could not get uptime information"
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        response = f"⏰ System Uptime:\n\n"
        
        if days > 0:
            response += f"📅 {days} days, {hours} hours, {minutes} minutes\n"
        elif hours > 0:
            response += f"⏰ {hours} hours, {minutes} minutes\n"
        else:
            response += f"⏰ {minutes} minutes\n"
        
        return response
    
    def _get_full_system_report(self) -> str:
        """Get comprehensive system report"""
        response = "📊 Complete System Report\n"
        response += "=" * 40 + "\n\n"
        
        # System info
        response += self._get_system_info() + "\n"
        
        # Health status
        response += self._get_system_health() + "\n"
        
        # CPU status
        response += self._get_cpu_status() + "\n"
        
        # Memory status
        response += self._get_memory_status() + "\n"
        
        # Disk status
        response += self._get_disk_status() + "\n"
        
        # Network status
        response += self._get_network_status() + "\n"
        
        # Battery status
        response += self._get_battery_status() + "\n"
        
        # Uptime
        response += self._get_uptime() + "\n"
        
        return response


# Global instance
system_monitor_feature = SystemMonitorFeature()


def handle_system_monitor_command(command: str) -> str:
    """Handle system monitor-related voice commands"""
    return system_monitor_feature.process_command(command)


if __name__ == "__main__":
    # Test the system monitor feature
    feature = SystemMonitorFeature()
    
    # Test commands
    test_commands = [
        "cpu usage",
        "memory usage",
        "system health",
        "system info"
    ]
    
    for cmd in test_commands:
        print(f"Command: {cmd}")
        print(f"Response: {feature.process_command(cmd)}")
        print("-" * 50) 