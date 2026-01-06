"""
Custom Exception Hierarchy for the College Attendance System.

This module provides a structured exception hierarchy with rich context
and meaningful error messages following professional coding practices.
"""

from typing import Any, Dict, Optional
from rest_framework import status


class BaseAttendanceError(Exception):
    """
    Base exception for all attendance system errors.
    
    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code for the error.
        details: Additional context about the error.
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the base attendance error.
        
        Args:
            message: Human-readable error message.
            status_code: HTTP status code (default: 500).
            details: Additional context dictionary.
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary format.
        
        Returns:
            Dictionary representation of the error.
        """
        return {
            "error": self.message,
            "code": self.status_code,
            "details": self.details
        }


class AuthenticationError(BaseAttendanceError):
    """
    Exception for authentication-related errors.
    """
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize authentication error.
        
        Args:
            message: Error message (default: "Authentication failed").
            details: Additional context dictionary.
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class ValidationError(BaseAttendanceError):
    """
    Exception for validation-related errors.
    """
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize validation error.
        
        Args:
            message: Error message (default: "Validation failed").
            field: Name of the field that failed validation.
            value: Value that failed validation.
            details: Additional context dictionary.
        """
        error_details: Dict[str, Any] = details or {}
        
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["value"] = str(value)
        
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=error_details
        )


class NotFoundError(BaseAttendanceError):
    """
    Exception for resource not found errors.
    """
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize not found error.
        
        Args:
            resource_type: Type of resource (e.g., "Student", "Class").
            resource_id: ID of the resource that was not found.
            details: Additional context dictionary.
        """
        message: str = f"{resource_type} not found"
        if resource_id is not None:
            message += f" (ID: {resource_id})"
        
        error_details: Dict[str, Any] = details or {}
        error_details["resource_type"] = resource_type
        if resource_id is not None:
            error_details["resource_id"] = str(resource_id)
        
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=error_details
        )


class DuplicateEntryError(BaseAttendanceError):
    """
    Exception for duplicate entry errors.
    """
    
    def __init__(
        self,
        resource_type: str,
        field: str,
        value: Any,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize duplicate entry error.
        
        Args:
            resource_type: Type of resource (e.g., "User", "Student").
            field: Field that has duplicate value.
            value: Duplicate value.
            details: Additional context dictionary.
        """
        message: str = (
            f"{resource_type} with {field}='{value}' already exists"
        )
        
        error_details: Dict[str, Any] = details or {}
        error_details["resource_type"] = resource_type
        error_details["field"] = field
        error_details["value"] = str(value)
        
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=error_details
        )


class PermissionError(BaseAttendanceError):
    """
    Exception for permission/authorization errors.
    """
    
    def __init__(
        self,
        message: str = "Permission denied",
        required_permission: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize permission error.
        
        Args:
            message: Error message (default: "Permission denied").
            required_permission: Permission that was required.
            details: Additional context dictionary.
        """
        error_details: Dict[str, Any] = details or {}
        
        if required_permission:
            error_details["required_permission"] = required_permission
        
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=error_details
        )


class ImageProcessingError(BaseAttendanceError):
    """
    Exception for image processing errors.
    """
    
    def __init__(
        self,
        message: str = "Image processing failed",
        image_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize image processing error.
        
        Args:
            message: Error message (default: "Image processing failed").
            image_type: Type of image operation.
            details: Additional context dictionary.
        """
        error_details: Dict[str, Any] = details or {}
        
        if image_type:
            error_details["image_type"] = image_type
        
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=error_details
        )


class FaceVerificationError(BaseAttendanceError):
    """
    Exception for face verification errors.
    """
    
    def __init__(
        self,
        message: str = "Face verification failed",
        student_id: Optional[int] = None,
        verification_result: Optional[bool] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize face verification error.
        
        Args:
            message: Error message (default: "Face verification failed").
            student_id: ID of the student being verified.
            verification_result: Result of verification.
            details: Additional context dictionary.
        """
        error_details: Dict[str, Any] = details or {}
        
        if student_id is not None:
            error_details["student_id"] = student_id
        if verification_result is not None:
            error_details["verified"] = verification_result
        
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=error_details
        )


class DatabaseError(BaseAttendanceError):
    """
    Exception for database-related errors.
    """
    
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        table: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize database error.
        
        Args:
            message: Error message (default: "Database operation failed").
            operation: Type of database operation.
            table: Name of the table.
            details: Additional context dictionary.
        """
        error_details: Dict[str, Any] = details or {}
        
        if operation:
            error_details["operation"] = operation
        if table:
            error_details["table"] = table
        
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


# Exception handler for Django REST Framework
def exception_handler(exc: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Custom exception handler for Django REST Framework.
    
    Args:
        exc: The exception that was raised.
        context: Additional context about the request.
        
    Returns:
        Response dictionary with error information.
    """
    if isinstance(exc, BaseAttendanceError):
        return exc.to_dict()
    
    # Handle other exceptions with a generic response
    return {
        "error": str(exc),
        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "details": {}
    }
