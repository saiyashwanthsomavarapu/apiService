from fastapi import HTTPException
from fastapi.exceptions import ValidationException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.auth.jwt import create_access_token
from app.auth.security import hash_password, verify_password
from app.core.error_utils import handle_db_errors
from app.db.models.user import User
from app.exceptions.booking_exceptions import UserNotFoundException
from app.exceptions.user_exceptions import AuthenticationException, EmailAlreadyExistsException, EmailNotFoundException
from app.schemas.user import LoginRequest, UserCreate

@handle_db_errors("create_user_query")
async def create_user_query(db: AsyncSession, user: UserCreate):
    
    if not user.email or not user.password:
        raise ValidationException("Email and password are required", 'email', 'password')

    existing_email = await db.execute(select(User).where(User.email == user.email))
    if existing_email.scalar_one_or_none():
        raise EmailAlreadyExistsException(user.email)
    
    try: 
        user_data = user.model_dump(exclude={"password"})
        user_data["hashed_password"] = hash_password(user.hashed_password)

        user_data = user.model_dump(exclude={"password"})
        user_data["hashed_password"] = hash_password(user.hashed_password)
        db_user = User(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    except IntegrityError as e:
        await db.rollback()
        raise EmailAlreadyExistsException(user.email)

@handle_db_errors("get_users_query")
async def get_users_query(db: AsyncSession):   
    result = await db.execute(select(User))
    return result.scalars().all()

@handle_db_errors("get_user_query")
async def get_user_query(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    if result.scalar_one_or_none():
        raise UserNotFoundException(user_id)
    return result.scalars().first()

@handle_db_errors("get_user_by_email_query")
async def get_user_by_email_query(db: AsyncSession, user_email: str):
    result = await db.execute(select(User).where(User.email == user_email))
    return result.scalars().first()

@handle_db_errors("login_user_query")
async def login_user_query(db: AsyncSession, user: LoginRequest):
    try:
        if not user.email or not user.password:
            raise ValidationException("Email and password are required", 'email', 'password')
        
        if "@" not in user.email:
            raise ValidationException("Invalid email format", 'email')
        
        db_user = await db.execute(select(User).where(User.email == user.email))
        result = db_user.scalar_one_or_none()

        if not user or not verify_password(user.password, result.hashed_password):
            raise AuthenticationException("Invalid email or password")
    
        access_token = create_access_token(data={"sub": result.email})
        return access_token

    except IntegrityError as e:
        await db.rollback()
        raise ValidationException("Data integrity constraint violation")