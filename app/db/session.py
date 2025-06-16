from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, 
    autocommit=False,
    autoflush=False, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
