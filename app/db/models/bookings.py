from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.models.base import Base
import enum


class BookingStatus(str, enum.Enum):
    """Booking status enumeration."""
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    PENDING = "pending"


class Bookings(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    time_slot_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    booked_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=func.now())
    
   # Relationships
    creator = relationship("User", back_populates="bookings", foreign_keys=[created_by])
    booked_event = relationship("Events", back_populates="bookings", foreign_keys=[time_slot_id])

    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.event_name}', start='{self.start_time}')>"
