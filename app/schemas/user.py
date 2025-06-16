from datetime import datetime
from typing import Optional 
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    firstname: str
    lastname: str
    hashed_password: str
    is_verified: bool
    is_admin: bool
    created_at: Optional[datetime] = datetime.now()
    modified_at: Optional[datetime] = datetime.now()


class UserOut(UserCreate):
    id: int

    class Config:
        orm_mode = True
    

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"