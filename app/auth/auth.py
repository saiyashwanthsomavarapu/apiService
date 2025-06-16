from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.jwt import verify_access_token
from app.core.error_utils import handle_db_errors
from app.db.operations.user import get_user_by_email_query
from app.db.session import get_db
from app.db.models.user import User
from app.exceptions.user_exceptions import AuthenticationException, EmailNotFoundException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
    
@handle_db_errors("get_current_user")
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Return the user corresponding to the given token.

    Args:
        token: The JWT token given by the client. If the token is invalid, a 401 error is raised.

    Returns:
        The user corresponding to the given token as a dictionary.
    """
    payload = verify_access_token(token)
   
    if not payload:
        raise AuthenticationException("Invalid token")
    user_detailas = await get_user_by_email_query(db, payload.get("sub"))


    if not user_detailas:
        raise EmailNotFoundException(payload.get("sub"))
    
    return  {
        "id": user_detailas.id,
        "lastname": user_detailas.lastname,
        "firstname": user_detailas.firstname,
        "email": user_detailas.email,
        "is_verified": user_detailas.is_verified,
        "is_admin": user_detailas.is_admin,
    }


async def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user['is_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def admin_or_user(current_user: User = Depends(get_current_user)):
    # You can also log or validate other roles here
    return current_user