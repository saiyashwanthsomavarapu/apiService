from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.operations.user import create_user_query, login_user_query
from app.schemas.user import Token, LoginRequest, UserCreate, UserOut

router = APIRouter()

@router.post('/login', response_model=Token)
async def login(login_req: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login_user_query(db, login_req)

@router.post("/register/", response_model=UserOut)
async def create(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user_query(db, user_data)
