from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class EventsCreate(BaseModel):
    event_name: str
    description: str
    start_time: datetime
    end_time: datetime
    status: str
    category_id: int
    created_by: Optional[int] = None
    created_at: Optional[datetime] = datetime.now()
    modified_at: Optional[datetime] = datetime.now()

class EventsUpdate(BaseModel):
    id: int
    event_name: str
    description: str
    start_time: datetime
    end_time: datetime
    status: str
    category_id: int

class EventsOut(EventsCreate):
    id: int

    class Config:
        orm_mode = True
