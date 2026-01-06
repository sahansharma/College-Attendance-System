"""
Logging Configuration for the College Attendance System.

This module provides centralized logging configuration for the application,
including formatters, handlers, and loggers for different components.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/attendance_system.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_logging: bool = True
) -> None:
    """
    Set up centralized logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        max_bytes: Maximum log file size in bytes
        backup_count: Number of backup log files to keep
        console_logging: Whether to enable console logging
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create handlers
    handlers = []

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    handlers.append(file_handler)

    # Console handler (optional)
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(simple_formatter)
        handlers.append(console_handler)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add our handlers
    for handler in handlers:
        root_logger.addHandler(handler)

    # Configure specific loggers for different modules
    _configure_module_loggers(numeric_level)


def _configure_module_loggers(level: int) -> None:
    """
    Configure specific loggers for different application modules.

    Args:
        level: Numeric logging level
    """
    # API module logger
    api_logger = logging.getLogger('api')
    api_logger.setLevel(level)

    # Admin app logger
    admin_logger = logging.getLogger('admin_app')
    admin_logger.setLevel(level)

    # Django logger (reduce noise)
    django_logger = logging.getLogger('django')
    django_logger.setLevel(logging.WARNING)

    # Face recognition logger
    face_logger = logging.getLogger('face_recognition')
    face_logger.setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class AttendanceSystemLogger:
    """
    Custom logger class for attendance system specific logging.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_request(self, method: str, path: str, user_id: Optional[int] = None) -> None:
        """
        Log API request details.

        Args:
            method: HTTP method
            path: Request path
            user_id: User ID if authenticated
        """
        user_info = f" (user_id={user_id})" if user_id else ""
        self.logger.info(f"Request: {method} {path}{user_info}")

    def log_authentication(self, action: str, username: str, success: bool) -> None:
        """
        Log authentication events.

        Args:
            action: Authentication action (login, logout, register)
            username: Username involved
            success: Whether authentication was successful
        """
        status = "successful" if success else "failed"
        self.logger.info(f"Authentication {action} {status} for user: {username}")

    def log_attendance(self, action: str, student_id: int, status: str) -> None:
        """
        Log attendance-related events.

        Args:
            action: Attendance action (marked, updated, deleted)
            student_id: Student ID
            status: Attendance status
        """
        self.logger.info(f"Attendance {action}: student_id={student_id}, status={status}")

    def log_error(self, error_type: str, message: str, exc_info: Optional[Exception] = None) -> None:
        """
        Log application errors.

        Args:
            error_type: Type of error
            message: Error message
            exc_info: Exception information
        """
        if exc_info:
            self.logger.error(f"{error_type}: {message}", exc_info=exc_info)
        else:
            self.logger.error(f"{error_type}: {message}")

    def log_performance(self, operation: str, duration: float, details: Optional[str] = None) -> None:
        """
        Log performance metrics.

        Args:
            operation: Operation name
            duration: Duration in seconds
            details: Additional details
        """
        detail_str = f" - {details}" if details else ""
        self.logger.info(f"Performance: {operation} took {duration:.3f}s{detail_str}")


# Global logger instance for convenience
attendance_logger = AttendanceSystemLogger('attendance_system')
