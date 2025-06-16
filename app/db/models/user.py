import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.db.models.base import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)
    modified_at = Column(DateTime, nullable=False)

    # Relationships
    created_categories = relationship("Category", back_populates="creator", foreign_keys="Category.created_by")
    created_events = relationship("Events", back_populates="creator", foreign_keys="Events.created_by")
    bookings = relationship("Bookings", back_populates="creator", foreign_keys="Bookings.created_by")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.firstname} {self.lastname}')>"
