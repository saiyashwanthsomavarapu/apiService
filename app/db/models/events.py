from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from app.db.models.base import Base
from sqlalchemy.orm import relationship

class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="NOT_BOOKED")
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    modified_at = Column(DateTime, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="events", foreign_keys=[category_id])
    creator = relationship("User", back_populates="created_events", foreign_keys=[created_by])
    bookings = relationship("Bookings", back_populates="booked_event", foreign_keys="Bookings.time_slot_id")

    
    def __repr__(self):
        return f"<Booking(id={self.id}, user_id={self.user_id}, event_id={self.event_id}, status='{self.status}')>"