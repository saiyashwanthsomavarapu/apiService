import logging
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.db.models import Base
from app.db.models.user import User
from app.auth.security import hash_password
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Handle database creation and initialization"""
    
    def __init__(self, database_url: str, database_name: str):
        self.database_url = database_url
        self.database_name = database_name
        self.server_url = database_url.rsplit('/', 1)[0]  # Remove database name
        
    async def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            # Convert async URL to sync URL for database creation
            sync_server_url = self.server_url.replace('asyncpg', 'psycopg2')
            if 'postgresql+asyncpg' in sync_server_url:
                sync_server_url = sync_server_url.replace('postgresql+asyncpg', 'postgresql+psycopg2')
            
            logger.info(f"Connecting to server: {sync_server_url}")
            sync_engine = create_engine(sync_server_url, isolation_level="AUTOCOMMIT")
            
            with sync_engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": self.database_name}
                )
                
                if not result.fetchone():
                    logger.info(f"Database '{self.database_name}' does not exist. Creating...")
                    # Use identifier quoting to handle special characters in database names
                    conn.execute(text(f'CREATE DATABASE "{self.database_name}"'))
                    logger.info(f"Database '{self.database_name}' created successfully")
                else:
                    logger.info(f"Database '{self.database_name}' already exists")
                    
            sync_engine.dispose()
            
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            raise

    async def create_tables(self):
        """Create all tables"""
        try:
            logger.info(f"Creating tables using URL: {self.database_url}")
            async_engine = create_async_engine(self.database_url, echo=True)  # Added echo for debugging
            
            async with async_engine.begin() as conn:
                # Import all models to ensure they're registered with Base
                # This is crucial - make sure all your model files are imported
                try:
                    # Import all your model modules here
                    from app.db.models import user  # Import your models
                    # Add other model imports as needed
                    logger.info("Models imported successfully")
                except ImportError as e:
                    logger.error(f"Error importing models: {e}")
                    raise
                
                # Create all tables
                await conn.run_sync(Base.metadata.create_all, checkfirst=True)
                logger.info("All tables created successfully")
                
                # Log created tables for debugging
                table_names = list(Base.metadata.tables.keys())
                logger.info(f"Created tables: {table_names}")
                
            await async_engine.dispose()
            
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def add_default_users(self, session: AsyncSession, default_users: List[Dict[str, Any]]):
        """Add default users to the database"""
        try:
            logger.info(f"Adding {len(default_users)} default users...")
            
            for user_data in default_users:
                logger.info(f"Processing user: {user_data.get('email', 'Unknown')}")
                
                # Use SQLAlchemy ORM instead of raw SQL for better compatibility
                from sqlalchemy import select
                
                # Check if user already exists using ORM
                stmt = select(User).where(User.email == user_data["email"])
                result = await session.execute(stmt)
                existing_user = result.scalar_one_or_none()
                
                if not existing_user:
                    # Create user
                    hashed_password = hash_password(user_data["password"])
                    user = User(
                        email=user_data["email"],
                        firstname=user_data.get("firstname"),  # Fixed field mapping
                        lastname=user_data.get("lastname", ""),
                        hashed_password=hashed_password,
                        is_admin=user_data.get("is_admin", True),
                        is_verified=user_data.get("is_verified", False),
                        created_at=datetime.now(),
                        modified_at=datetime.now()
                    )
                    
                    session.add(user)
                    logger.info(f"Added default user: {user_data['email']}")
                else:
                    logger.info(f"User already exists: {user_data['email']}")
            
            await session.commit()
            logger.info("Default users processed successfully")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error adding default users: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def verify_tables_created(self):
        """Verify that tables were created successfully"""
        try:
            async_engine = create_async_engine(self.database_url)
            
            async with async_engine.begin() as conn:
                # Get list of tables
                result = await conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"Tables in database: {tables}")
                
                if not tables:
                    logger.warning("No tables found in database!")
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"Error verifying tables: {str(e)}")
            return False