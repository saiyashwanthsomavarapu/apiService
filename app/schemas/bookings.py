from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class BookingsCreate(BaseModel):
    time_slot_id: int
    created_by: Optional[int] = None
    booked_at: Optional[datetime] = datetime.now()
    created_at: Optional[datetime] = datetime.now()
    modified_at: Optional[datetime] = datetime.now()

class BookingOut(BookingsCreate):
    id: int
    
    class Config:
        orm_mode = True