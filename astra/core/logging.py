"""
Logging configuration for Astra voice assistant.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from .config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record):
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


class AstraLogger:
    """Main logger for Astra application."""
    
    def __init__(self, name: str = "astra"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up logging handlers."""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        if settings.log_format == "json":
            console_formatter = StructuredFormatter()
        else:
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for all logs
        log_file = settings.logs_dir / f"astra_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_file = settings.logs_dir / f"astra_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
        
        # Enterprise audit logging
        if settings.is_enterprise:
            audit_file = settings.logs_dir / f"astra_audit_{datetime.now().strftime('%Y%m%d')}.log"
            audit_handler = logging.FileHandler(audit_file)
            audit_handler.setLevel(logging.INFO)
            audit_handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(audit_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log_with_extra(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_with_extra(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_extra(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log_with_extra(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log_with_extra(logging.CRITICAL, message, **kwargs)
    
    def _log_with_extra(self, level: int, message: str, **kwargs):
        """Log message with extra fields."""
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0, message, (), None
        )
        if kwargs:
            record.extra_fields = kwargs
        self.logger.handle(record)
    
    def audit(self, action: str, user: str, resource: str, **kwargs):
        """Log audit event (Enterprise only)."""
        if settings.is_enterprise:
            audit_data = {
                "action": action,
                "user": user,
                "resource": resource,
                "timestamp": datetime.utcnow().isoformat(),
                "ip_address": kwargs.get("ip_address"),
                "user_agent": kwargs.get("user_agent"),
                "session_id": kwargs.get("session_id"),
            }
            self.info("AUDIT_EVENT", **audit_data)
    
    def security(self, event: str, **kwargs):
        """Log security event."""
        security_data = {
            "security_event": event,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        self.warning("SECURITY_EVENT", **security_data)


def setup_logging(name: str = "astra") -> AstraLogger:
    """Set up and return Astra logger."""
    return AstraLogger(name)


def get_logger(name: str = "astra") -> AstraLogger:
    """Get Astra logger instance."""
    return AstraLogger(name)


# Global logger instance
logger = setup_logging() 