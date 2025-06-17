from datetime import datetime
from sqlalchemy import case, delete, null, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError

from app.db.models.events import Events
from app.schemas.events import EventsCreate, EventsUpdate
from app.db.models.bookings import Bookings
from app.db.models.categories import Category
from app.db.models.user import User
from app.exceptions.event_exceptions import (
    EventNotFoundException,
    EventHasBookingsException,
    ValidationException
)
from app.core.error_utils import handle_db_errors

@handle_db_errors("create_event_query")
async def create_event_query(db: AsyncSession, event: EventsCreate, user_id: int):
    try:
        # Validate user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        if not user_result.scalar_one_or_none():
            raise ValidationException("Invalid user ID", "user_id")
        
        # Validate category exists if provided
        if event.category_id:
            category_result = await db.execute(select(Category).where(Category.id == event.category_id))
            if not category_result.scalar_one_or_none():
                raise ValidationException("Invalid category ID", "category_id")
        
        # Create event
        event_data = event.model_dump()
        event_data["created_by"] = user_id
        db_event = Events(**event_data)
        
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        
        return db_event
        
    except IntegrityError as e:
        await db.rollback()
        raise ValidationException("Data integrity constraint violation")

@handle_db_errors("get_event_by_id_query")
async def get_event_by_id_query(db: AsyncSession, event_id: int):
    if event_id <= 0:
        raise ValidationException("Event ID must be positive", "event_id")
    
    result = await db.execute(select(Events).where(Events.id == event_id))
    event = result.scalars().first()
    
    if not event:
        raise EventNotFoundException(event_id)
    
    return event

@handle_db_errors("get_events_query")
async def get_events_query(db: AsyncSession):
    slots = aliased(Bookings)
    category = aliased(Category)
    event = Events

    result = await db.execute(
        select(
            event.status,
            case(
                (event.status == "BOOKED", slots.created_by),
                else_=null()
            ).label("user_id"),
            event.id,
            category.category_name,
            event.event_name,
            event.start_time,
            event.end_time,
            event.description
        )
        .select_from(event)
        .outerjoin(slots, event.id == slots.time_slot_id)
        .outerjoin(category, event.category_id == category.id)
    )
    
    return {"data": result.mappings().all()}

@handle_db_errors("update_event_query")
async def update_event_query(db: AsyncSession, event: EventsUpdate):
    if not event.id or event.id <= 0:
        raise ValidationException("Valid event ID is required", "id")
    
    # Validate category if provided
    if event.category_id:
        category_result = await db.execute(select(Category).where(Category.id == event.category_id))
        if not category_result.scalar_one_or_none():
            raise ValidationException("Invalid category ID", "category_id")
    
    # Build update data
    update_data = {}
    if event.event_name is not None:
        update_data["event_name"] = event.event_name
    if event.start_time is not None:
        update_data["start_time"] = event.start_time
    if event.end_time is not None:
        update_data["end_time"] = event.end_time
    if event.description is not None:
        update_data["description"] = event.description
    if event.category_id is not None:
        update_data["category_id"] = event.category_id
    
    if not update_data:
        raise ValidationException("No fields to update provided")
    
    update_data['modified_at'] = datetime.now()

    result = await db.execute(
        update(Events)
        .where(Events.id == event.id)
        .values(**update_data)
    )
    
    if result.rowcount == 0:
        raise EventNotFoundException(event.id)
    
    await db.commit()
    
    return {"message": "Event updated successfully", "event_id": event.id}

@handle_db_errors("delete_event_query")
async def delete_event_query(db: AsyncSession, event_id: int):

    if event_id <= 0:
        raise ValidationException("Event ID must be positive", "event_id")
    
    # Check for existing bookings
    booking_count_result = await db.execute(
        select(func.count(Bookings.id)).where(Bookings.time_slot_id == event_id)
    )
    booking_count = booking_count_result.scalar()
    
    if booking_count > 0:
        raise EventHasBookingsException(event_id, booking_count)
    
    # Delete the event
    result = await db.execute(delete(Events).where(Events.id == event_id))
    
    if result.rowcount == 0:
        raise EventNotFoundException(event_id)
    
    await db.commit()
    
    return {"message": "Event deleted successfully", "event_id": event_id}