from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.auth import admin_required, get_current_user
from app.db.operations.bookings import cancel_booking_query, create_booking_query
from app.db.operations.events import get_events_query
from app.schemas.bookings import BookingsCreate
from app.schemas.user import UserCreate, UserOut
from app.db.session import get_db
from app.db.operations.user import create_user_query, get_users_query, get_user_query
from app.auth.auth import admin_required
from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.schemas.events import EventsCreate, EventsUpdate
from app.db.operations.categories import create_category_query, get_categories_query, delete_category_by_id_query, get_category_by_id_query, update_category_query
from app.db.operations.events import create_event_query, delete_event_query, update_event_query

router = APIRouter()

@router.get("/me")
async def get_my_info(user=Depends(get_current_user)):
    return user

@router.get("/users", response_model=list[UserOut])
async def read_users(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await get_users_query(db)

@router.get("/users/{user_id}", response_model=UserOut)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await get_user_query(db, user_id)

@router.post('/reserve_slot')
async def book_slot(slot: BookingsCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await create_booking_query(db, slot, user['id'])

@router.get('/all_slots')
async def read_bookings(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await get_events_query(db)

@router.delete('/cancel_slot/{event_id}')
async def cancel_slot(event_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await cancel_booking_query(db, event_id, user['id'])


@router.post('/categories')
async def add_category(catgory: CategoryCreate, db: AsyncSession = Depends(get_db),  user=Depends(admin_required)):
    return await create_category_query(db, catgory, user['id'])

@router.get('/categories')
async def read_categories(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await get_categories_query(db)

@router.get('/categories/{catgory_id}')
async def read_categories_by_id(category_id: int, db: AsyncSession = Depends(get_db),  user=Depends(admin_required)):
    return await get_category_by_id_query(db, category_id)

@router.put('/category')
async def update_category_route(category: CategoryUpdate, db: AsyncSession = Depends(get_db),  user=Depends(admin_required)): 
    return await update_category_query(db, category)

@router.delete('/category/{category_id}')
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db), user=Depends(admin_required)):
    return await delete_category_by_id_query(db, category_id)

@router.post('/create_event')
async def add_event(event: EventsCreate, db: AsyncSession = Depends(get_db),  user=Depends(admin_required)):
    return await create_event_query(db, event, user['id'])

@router.delete('/event/{event_id}')
async def delete_event_route(event_id: int, db: AsyncSession = Depends(get_db), user=Depends(admin_required)):
    return await delete_event_query(db, event_id)

@router.put('/event')
async def update_event_route(event: EventsUpdate, db: AsyncSession = Depends(get_db),  user=Depends(admin_required)):
    return await update_event_query(db, event)
