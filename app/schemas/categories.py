from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CategoryCreate(BaseModel):
    category_name: str
    color: str
    created_by: Optional[int] = None
    created_at: Optional[datetime] = datetime.now()
    modified_at: Optional[datetime] = datetime.now()

class CategoryUpdate(BaseModel):
    id: int
    category_name: str
    color: str

class CategoryOut(CategoryCreate):
    id: int

    class Config:
        orm_mode = True
