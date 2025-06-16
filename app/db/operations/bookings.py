from sqlalchemy import delete, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError

from app.db.models.bookings import Bookings
from app.db.models.categories import Category
from app.db.models.events import Events
from app.db.models.user import User
from app.schemas.bookings import BookingsCreate
from app.exceptions.booking_exceptions import (
    BookingNotFoundException,
    TimeSlotAlreadyBookedException,
    TimeSlotNotFoundException,
    BookingNotOwnedException,
    UserNotFoundException
)
from app.exceptions.event_exceptions import ValidationException
from app.core.error_utils import handle_db_errors


@handle_db_errors("create_booking_query")
async def create_booking_query(db: AsyncSession, booking: BookingsCreate, user_id: int):
  
    # Validate input
    if not booking.time_slot_id or booking.time_slot_id <= 0:
        raise ValidationException("Valid time slot ID is required", "time_slot_id")
    
    if not user_id or user_id <= 0:
        raise ValidationException("Valid user ID is required", "user_id")
    
    # Check if user exists
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise UserNotFoundException(user_id)
    
    # Check if time slot (event) exists and get its current status
    event_result = await db.execute(
        select(Events).where(Events.id == booking.time_slot_id)
    )
    event = event_result.scalar_one_or_none()
    if not event:
        raise TimeSlotNotFoundException(booking.time_slot_id)
    
    # Check if time slot is available for booking
    if event.status == "BOOKED":
        raise TimeSlotAlreadyBookedException(booking.time_slot_id)
    
    # Check if user already has a booking for this time slot
    existing_user_booking = await db.execute(
        select(Bookings).where(
            and_(
                Bookings.time_slot_id == booking.time_slot_id,
                Bookings.created_by == user_id
            )
        )
    )
    if existing_user_booking.scalar_one_or_none():
        raise ValidationException("You already have a booking for this time slot")
    
    # Check for any existing booking (double-check for race conditions)
    existing_booking_result = await db.execute(
        select(Bookings).where(Bookings.time_slot_id == booking.time_slot_id)
    )
    existing_booking = existing_booking_result.scalar_one_or_none()
    if existing_booking:
        raise TimeSlotAlreadyBookedException(booking.time_slot_id)
    
    try:
        # Create the booking
        booking_data = booking.model_dump()
        booking_data["created_by"] = user_id

        db_booking = Bookings(**booking_data)
        db.add(db_booking)
        
        # Update event status to BOOKED
        update_result = await db.execute(
            update(Events)
            .where(Events.id == booking.time_slot_id)
            .values(status="BOOKED")
        )
        
        if update_result.rowcount == 0:
            raise TimeSlotNotFoundException(booking.time_slot_id)
        
        await db.commit()
        await db.refresh(db_booking)
        
        return db_booking
        
    except IntegrityError as e:
        await db.rollback()
        raise TimeSlotAlreadyBookedException(booking.time_slot_id)

@handle_db_errors("get_bookings_by_user_query")
async def get_bookings_by_user_query(db: AsyncSession, user_id: int):
    
    if not user_id or user_id <= 0:
        raise ValidationException("Valid user ID is required", "user_id")

    # Check if user exists
    user_result = await db.execute(select(User).where(User.id == user_id))
    if not user_result.scalar_one_or_none():
        raise UserNotFoundException(user_id)
    
    slots = Bookings
    user = aliased(User)
    category = aliased(Category)
    event = aliased(Events)

    result = await db.execute(
        select(
            event.status,
            user.id.label("user_id"),
            user.firstname,
            user.lastname,
            user.email,
            category.category_name,
            event.event_name,
            event.start_time,
            event.end_time,
            event.description,
            slots.id.label("booking_id"),
            slots.created_at.label("booking_date")
        )
        .select_from(slots)
        .join(user, slots.created_by == user.id)
        .join(event, slots.time_slot_id == event.id)
        .outerjoin(category, event.category_id == category.id)  # Use outerjoin in case category is null
        .where(slots.created_by == user_id)
        .order_by(slots.id.desc())
    )
    
    bookings = result.mappings().all()
    
    return {
        "data": bookings,
        "user_id": user_id
    }

@handle_db_errors("cancel_booking_query")
async def cancel_booking_query(db: AsyncSession, event_id: int, user_id: int):
    if not event_id or event_id <= 0:
        raise ValidationException("Valid event ID is required", "event_id")
    
    if not user_id or user_id <= 0:
        raise ValidationException("Valid user ID is required", "user_id")
    

    # Check if user exists
    user_result = await db.execute(select(User).where(User.id == user_id))
    if not user_result.scalar_one_or_none():
        raise UserNotFoundException(user_id)
    
    # Check if event exists
    event_result = await db.execute(select(Events).where(Events.id == event_id))
    event = event_result.scalar_one_or_none()
    if not event:
        raise TimeSlotNotFoundException(event_id)
    
    # Find the booking
    booking_result = await db.execute(
        select(Bookings).where(
            and_(
                Bookings.time_slot_id == event_id,
                Bookings.created_by == user_id
            )
        )
    )
    booking = booking_result.scalar_one_or_none()
    
    if not booking:
        # Check if booking exists for this time slot but for different user
        other_booking_result = await db.execute(
            select(Bookings).where(Bookings.time_slot_id == event_id)
        )
        other_booking = other_booking_result.scalar_one_or_none()
        
        if other_booking:
            raise BookingNotOwnedException(other_booking.id, user_id)
        else:
            raise BookingNotFoundException(f"No booking found for event {event_id}")
    
    try:
        # Delete the booking
        delete_result = await db.execute(
            delete(Bookings).where(
                and_(
                    Bookings.time_slot_id == event_id,
                    Bookings.created_by == user_id
                )
            )
        )
        
        if delete_result.rowcount == 0:
            raise BookingNotFoundException(f"Failed to cancel booking for event {event_id}")
        
        # Update event status back to available
        update_result = await db.execute(
            update(Events)
            .where(Events.id == event_id)
            .values(status="NOT_BOOKED")  # or "AVAILABLE" based on your logic
        )
        
        if update_result.rowcount == 0:
            # Rollback if event update fails
            await db.rollback()
            raise TimeSlotNotFoundException(event_id)
        
        await db.commit()

        return {
            "message": "Booking cancelled successfully",
            "event_id": event_id,
            "user_id": user_id,
        }
        
    except Exception as e:
        await db.rollback()
        raise