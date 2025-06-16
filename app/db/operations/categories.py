from datetime import datetime
from fastapi.exceptions import ValidationException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, delete, func, update
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError

from app.core.error_utils import handle_db_errors
from app.db.models.categories import Category
from app.db.models.events import Events
from app.db.models.user import User
from app.exceptions.booking_exceptions import UserNotFoundException
from app.exceptions.category_exceptions import CategoryAlreadyExistsException, CategoryCreationException, CategoryHasEventException, CategoryNotFoundException, CategoryUpdateException
from app.schemas.categories import CategoryCreate, CategoryUpdate

@handle_db_errors("create_category_query")
async def create_category_query(db: AsyncSession, category: CategoryCreate, user_id: int):
   
    if not category.category_name or not category.category_name.strip():
        raise ValidationException("Category name is required and cannot be empty", "category_name")
    
    if len(category.category_name.strip()) < 2:
        raise ValidationException("Category name must be at least 2 characters long", "category_name")
    
    if len(category.category_name.strip()) > 100:
        raise ValidationException("Category name cannot exceed 100 characters", "category_name")
    
    if not user_id or user_id <= 0:
        raise ValidationException("Valid user ID is required", "user_id")
    
    normalized_name = category.category_name.strip().title()

    user_result = await db.execute(select(User).where(User.id == user_id))
    if not user_result.scalar_one_or_none():
        raise UserNotFoundException(user_id)
    
    existing_category_result = await db.execute(select(Category).where(
        func.lower(Category.category_name) == func.lower(normalized_name)))
    
    existing_category = existing_category_result.scalar_one_or_none()
    if existing_category:
        raise CategoryAlreadyExistsException(normalized_name)
    
    try:
        category_data = category.model_dump()
        category_data["created_by"] = user_id
        category_data["category_name"] = normalized_name

        db_category = Category(**category_data)
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return db_category
    except IntegrityError as e:
        await db.rollback()

        if 'unique' in str(e).lower() or "duplicate" in str(e).lower():
            raise CategoryAlreadyExistsException(normalized_name)
        elif 'foreign' in str(e).lower():
            raise UserNotFoundException(user_id)
        else:
            raise CategoryCreationException(f"Database constraint violation: {str(e)}")

@handle_db_errors("get_categories_query")
async def get_categories_query(db: AsyncSession):
    category = aliased(Category)
    event = aliased(Events)
    result = await db.execute(  select(
            category.id,
            category.category_name,
            category.color,
            category.created_by.label("user_id"),
            func.count(event.id).label("event_count")
        )
        .outerjoin(event, event.category_id == category.id)
        .group_by(category.id)
        .order_by(category.created_at.desc()))
    categories = [
        {
            "id": row.id,
            "category_name": row.category_name,
            "color": row.color,
            "user_id": row.user_id,
            "event_count": row.event_count
        }
        for row in result.all()
    ]
    return {"data": categories}

@handle_db_errors("get_category_by_id_query")
async def get_category_by_id_query(db: AsyncSession, category_id: int):
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalars().first()

@handle_db_errors("update_category_query")
async def update_category_query(db: AsyncSession, category: CategoryUpdate):
    if  not category.id or category.id <= 0:
        raise ValidationException("Valid category ID is required", "id")

    if category.category_name is not None:
        if not category.category_name.strip():
            raise ValidationException("Category name  cannot be empty", "category_name")
        
        if len(category.category_name.strip()) < 2:
            raise ValidationException("Category name must be at least 2 characters long", "category_name")
        
        if len(category.category_name.strip()) > 100:
            raise ValidationException("Category name cannot exceed 100 characters", "category_name")
        
        normalized_name = category.category_name.strip().title()

        existing_category_result = await db.execute(select(Category).where(
            and_(
                func.lower(Category.category_name) == func.lower(normalized_name),
                Category.id != category.id
            )
        ))
        if existing_category_result.scalar_one_or_none():
            raise CategoryAlreadyExistsException(normalized_name)
        
    try: 
        update_data = {}
        if category.category_name is not None:
            update_data["category_name"] = normalized_name
        if category.color is not None:
            update_data["color"] = category.color

        update_data["modified_at"] = datetime.now()

        if not update_data:
            raise ValidationException("No fields to update provided")
        
        result = await db.execute(
            update(Category)
            .where(Category.id == category.id)
            .values(**update_data)
        )
        
        if result.rowcount == 0:
            raise CategoryNotFoundException(category.id)
        
        await db.commit()

        return {
            "message": "Category updated successfully",
            "category_id": category.id,
        }
    except IntegrityError as e:
        await db.rollback()
        if 'unique' in str(e).lower() or "duplicate" in str(e).lower():
            raise CategoryAlreadyExistsException(normalized_name)
        else:
            raise CategoryUpdateException(f"Database constraint violation: {str(e)}")


@handle_db_errors("delete_category_by_id_query")
async def delete_category_by_id_query(db: AsyncSession, category_id: int):
    
    if not category_id or category_id <= 0:
        raise ValidationException("Valid category ID is required", "category_id")
    
    event_count_result = await db.execute(
        select(func.count(Events.id)).where(Events.category_id == category_id)
    )
    event_count = event_count_result.scalar()
    if event_count > 0:
        raise CategoryHasEventException(category_id, event_count)
    try:
        result = await db.execute(delete(Category).where(Category.id == category_id))
        
        if result.rowcount == 0:
            raise CategoryNotFoundException(category_id)
        
        await db.commit()
        return {"data": {"message": "Category deleted successfully", "category_id": category_id}}
    except IntegrityError as e:
        await db.rollback()
        if 'foreign' in str(e).lower():
            raise CategoryNotFoundException(category_id)
        else:
            raise CategoryUpdateException(f"Database constraint violation: {str(e)}")