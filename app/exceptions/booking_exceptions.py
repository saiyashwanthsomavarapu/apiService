from app.exceptions.event_exceptions import BaseCustomException
from fastapi import status

class BookingNotFoundException(BaseCustomException):
    def __init__(self, booking_id: int):
        super().__init__(
            message=f"Booking with ID {booking_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"booking_id": booking_id}
        )

class TimeSlotAlreadyBookedException(BaseCustomException):
    def __init__(self, time_slot_id: int):
        super().__init__(
            message="This time slot is already booked",
            status_code=status.HTTP_409_CONFLICT,
            details={"time_slot_id": time_slot_id}
        )

class TimeSlotNotFoundException(BaseCustomException):
    def __init__(self, time_slot_id: int):
        super().__init__(
            message=f"Time slot with ID {time_slot_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"time_slot_id": time_slot_id}
        )

class BookingNotOwnedException(BaseCustomException):
    def __init__(self, booking_id: int, user_id: int):
        super().__init__(
            message="You can only cancel your own bookings",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"booking_id": booking_id, "user_id": user_id}
        )

class UserNotFoundException(BaseCustomException):
    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with ID {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"user_id": user_id}
        )

class InvalidTimeSlotStatusException(BaseCustomException):
    def __init__(self, time_slot_id: int, current_status: str):
        super().__init__(
            message=f"Time slot is not available for booking (current status: {current_status})",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"time_slot_id": time_slot_id, "current_status": current_status}
        )