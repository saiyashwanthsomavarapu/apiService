from fastapi import status
from  typing import Optional, Dict, Any

class UserNotFoundException(BaseException):
    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with ID {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"user_id": user_id}
        )

class UserAlreadyExistsException(BaseException):
    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with ID {user_id} already exists",
            status_code=status.HTTP_409_CONFLICT,
            details={"user_id": user_id}
        )
    
class EmailAlreadyExistsException(BaseException):
    def __init__(self, email: str):
        super().__init__(
            message=f"User with email {email} already exists",
            status_code=status.HTTP_409_CONFLICT,
            details={"email": email}
        )
    
class EmailNotFoundException(BaseException):
    def __init__(self, email: str):
        super().__init__(
            message=f"User with email {email} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"email": email}
        )


class AuthenticationException(BaseException):
    def __init__(self, message: str):
        super().__init__(
            message=message, 
            status_code=status.HTTP_401_UNAUTHORIZED, 
            details={"message": message}
        )