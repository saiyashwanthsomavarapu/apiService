from sqlalchemy import Column, ForeignKey, Integer, DateTime, String
from app.db.models.base import Base
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "category"
    
    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False) 
    created_at = Column(DateTime, nullable=False)
    modified_at = Column(DateTime, nullable=False)

    creator = relationship("User", back_populates="created_categories", foreign_keys=[created_by])
    events = relationship("Events", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.category_name}')>"