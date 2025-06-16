from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.init_db import DatabaseInitializer
from app.routes import router, user_router
from app.db.models.base import Base
from app.db.session import AsyncSessionLocal, engine
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions.event_exceptions import BaseCustomException
from app.exceptions.handlers import (
    custom_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
    http_exception_handler
)

settings = get_settings()

async def init_database():
    try: 
        print(settings.database_url)
        db_init = DatabaseInitializer(
            database_url=settings.database_url,
            database_name=settings.POSTGRES_DB
        )
        await db_init.create_database_if_not_exists()

        await db_init.create_tables()

        async with AsyncSessionLocal() as session:
            await db_init.add_default_users(session, settings.DEFAULT_USERS)

        print("Database initialized successfully")
    
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    pass



app = FastAPI(lifespan=lifespan)

# lifespan(app)

# CORS and Middleware
origins = [
    "http://localhost",
    "http://localhost:4200",  
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(BaseCustomException, custom_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Routes
app.include_router(router)
app.include_router(user_router)
