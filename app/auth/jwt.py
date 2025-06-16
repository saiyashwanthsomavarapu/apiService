# utils/jwt.py
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.core.config import get_settings

# Use a strong secret key in production!
settings = get_settings()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return {"access_token": jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM), "token_type": "bearer", "exp": expire}

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
