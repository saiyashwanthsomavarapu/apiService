from fastapi import  status
from typing import Optional, Dict, Any

class BaseCustomException(Exception):
    """Base exception class for custom exceptions"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class EventNotFoundException(BaseCustomException):
    def __init__(self, event_id: int):
        super().__init__(
            message=f"Event with ID {event_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"event_id": event_id}
        )

class EventHasBookingsException(BaseCustomException):
    def __init__(self, event_id: int, booking_count: int):
        super().__init__(
            message="Cannot delete event with existing bookings",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"event_id": event_id, "booking_count": booking_count}
        )

class DatabaseOperationException(BaseCustomException):
    def __init__(self, operation: str, original_error: str):
        super().__init__(
            message=f"Database error during {operation}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"operation": operation, "error": original_error}
        )

class ValidationException(BaseCustomException):
    def __init__(self, message: str, field: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"field": field} if field else {}
        )