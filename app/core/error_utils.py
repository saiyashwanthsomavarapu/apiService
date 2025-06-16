import logging
from functools import wraps
from typing import Callable, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions.event_exceptions import DatabaseOperationException

logger = logging.getLogger(__name__)

def handle_db_errors(operation_name: str):
    """Decorator to handle database errors"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            db_session: Optional[AsyncSession] = None
            
            # Find the database session in arguments
            for arg in args:
                if isinstance(arg, AsyncSession):
                    db_session = arg
                    break
            
            if not db_session:
                for key, value in kwargs.items():
                    if isinstance(value, AsyncSession):
                        db_session = value
                        break
            
            try:
                return await func(*args, **kwargs)
            except SQLAlchemyError as e:
                if db_session:
                    await db_session.rollback()
                logger.error(f"Database error in {operation_name}: {str(e)}")
                raise DatabaseOperationException(operation_name, str(e))
            except Exception as e:
                if db_session:
                    await db_session.rollback()
                logger.error(f"Unexpected error in {operation_name}: {str(e)}")
                raise
        
        return wrapper
    return decorator