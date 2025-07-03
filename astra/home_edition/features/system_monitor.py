import psutil
import platform
import datetime
from typing import Dict, Any

def get_system_metrics() -> Dict[str, Any]:
    """
    Retrieves various system performance metrics.

    Returns:
        A dictionary containing CPU, memory, disk, and network usage, and system uptime.
    """
    metrics = {}

    # CPU Usage
    metrics["cpu_percent"] = psutil.cpu_percent(interval=1)
    metrics["cpu_cores_physical"] = psutil.cpu_count(logical=False)
    metrics["cpu_cores_logical"] = psutil.cpu_count(logical=True)

    # Memory Usage
    virtual_memory = psutil.virtual_memory()
    metrics["memory_total_gb"] = round(virtual_memory.total / (1024**3), 2)
    metrics["memory_available_gb"] = round(virtual_memory.available / (1024**3), 2)
    metrics["memory_used_percent"] = virtual_memory.percent

    # Disk Usage (for the root partition)
    disk_usage = psutil.disk_usage('/')
    metrics["disk_total_gb"] = round(disk_usage.total / (1024**3), 2)
    metrics["disk_used_gb"] = round(disk_usage.used / (1024**3), 2)
    metrics["disk_free_gb"] = round(disk_usage.free / (1024**3), 2)
    metrics["disk_used_percent"] = disk_usage.percent

    # Network Activity (total sent/received since boot)
    net_io = psutil.net_io_counters()
    metrics["network_bytes_sent_gb"] = round(net_io.bytes_sent / (1024**3), 2)
    metrics["network_bytes_recv_gb"] = round(net_io.bytes_recv / (1024**3), 2)

    # System Uptime
    boot_time_timestamp = psutil.boot_time()
    boot_time_datetime = datetime.datetime.fromtimestamp(boot_time_timestamp)
    uptime_seconds = (datetime.datetime.now() - boot_time_datetime).total_seconds()
    metrics["system_uptime_days"] = int(uptime_seconds // (24 * 3600))
    metrics["system_uptime_hours"] = int((uptime_seconds % (24 * 3600)) // 3600)
    metrics["system_uptime_minutes"] = int((uptime_seconds % 3600) // 60)

    # Platform Information
    metrics["system_os"] = platform.system()
    metrics["system_release"] = platform.release()
    metrics["system_version"] = platform.version()
    metrics["system_machine"] = platform.machine()
    metrics["system_processor"] = platform.processor()

    return metrics

def get_running_processes(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieves a list of running processes.

    Args:
        limit: The maximum number of processes to return.

    Returns:
        A list of dictionaries, each representing a process.
    """
    processes = []
    for i, proc in enumerate(psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent'])):
        if i >= limit:
            break
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'username', 'cpu_percent', 'memory_percent'])
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes