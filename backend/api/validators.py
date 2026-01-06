"""
Validation Utilities for the College Attendance System.

This module provides reusable validation functions for input data
validation across the application.
"""

import re
from typing import Optional, Tuple


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format.

    Args:
        email: Email address to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not email:
        return False, "Email is required"

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_regex, email):
        return False, "Invalid email format"

    return True, None


def validate_password(password: str, min_length: int = 8) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Args:
        password: Password to validate.
        min_length: Minimum password length.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not password:
        return False, "Password is required"

    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format.

    Args:
        username: Username to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not username:
        return False, "Username is required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    if len(username) > 30:
        return False, "Username must be less than 30 characters"

    # Username can only contain letters, numbers, and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"

    return True, None


def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, Optional[str]]:
    """
    Validate name field.

    Args:
        name: Name to validate.
        field_name: Name of the field for error messages.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not name:
        return False, f"{field_name} is required"

    if len(name) < 2:
        return False, f"{field_name} must be at least 2 characters"

    if len(name) > 100:
        return False, f"{field_name} must be less than 100 characters"

    return True, None


def validate_date_range(
    start_date: str,
    end_date: str,
    date_format: str = "%Y-%m-%d"
) -> Tuple[bool, Optional[str]]:
    """
    Validate date range.

    Args:
        start_date: Start date string.
        end_date: End date string.
        date_format: Date format string.

    Returns:
        Tuple of (is_valid, error_message).
    """
    try:
        from datetime import datetime

        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)

        if start > end:
            return False, "Start date must be before end date"

        return True, None

    except ValueError:
        return False, "Invalid date format"


def validate_image_file(
    file_obj,
    allowed_types: tuple = ('image/jpeg', 'image/png', 'image/gif'),
    max_size_mb: int = 5
) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded image file.

    Args:
        file_obj: Uploaded file object.
        allowed_types: Tuple of allowed MIME types.
        max_size_mb: Maximum file size in MB.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not file_obj:
        return False, "File is required"

    # Check file type
    if file_obj.content_type not in allowed_types:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_types)}"

    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_size_bytes:
        return False, f"File size exceeds {max_size_mb}MB limit"

    return True, None


def sanitize_input(input_str: str) -> str:
    """
    Sanitize string input by removing potentially harmful characters.

    Args:
        input_str: String to sanitize.

    Returns:
        Sanitized string.
    """
    if not input_str:
        return ""

    # Remove any HTML/script tags
    sanitized = re.sub(r'<[^>]*>', '', input_str)

    # Remove extra whitespace
    sanitized = ' '.join(sanitized.split())

    return sanitized
