from app.exceptions.event_exceptions import BaseCustomException
from fastapi import status

class CategoryNotFoundException(BaseCustomException):
    def __init__(self, category_id: int):
        super().__init__(
            message=f"Category with ID {category_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"category_id": category_id}
        )

class CategoryAlreadyExistsException(BaseCustomException):
    def __init__(self, category_name: str):
        super().__init__(
            message=f"Category with name {category_name} already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"category_name": category_name}
        )

class CategoryHasEventException(BaseCustomException):
    def __init__(slef, category_id: int, event_count:int):
        super().__init__(
            message="Cannot delete category with existing events",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"category_id": category_id, "event_count": event_count}
        )

class CategoryCreationException(BaseCustomException):
    def __init__(self, message: str):
        super().__init__(
            message=f"Failed to create category: {message}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"message": message}
        )

class CategoryUpdateException(BaseCustomException):
    def __init__(self, category_id: int,message: str):
        super().__init__(
            message=f"Failed to update category: {message}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"message": message, "category_id": category_id}
        )