from functools import lru_cache
import os

class Settings():
    # Application settings
    APP_NAME: str = "Event Booking System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database settings
    POSTGRES_USER: str = "postgres"
    # POSTGRES_PASSWORD: str = "password123"
    POSTGRES_PASSWORD: str = "postgres" 
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "mydb"
    
    # Security settings
    SECRET_KEY: str = "secretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    
    # Logging settings
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Database connection pool settings


    api_v1_prefix: str = "/api/v1"

    DEFAULT_USERS: list = [
        {
            "email": "admin@example.com",
            "password": "admin123",
            "firstname": "admin",
            "lastname": "System Administrator",
            "is_admin": True,
            "is_verified": True
        },
        {
            "email": "user@example.com", 
            "password": "user123",
            "firstname": "user",
            "lastname": "Regular User",
            "is_verified": True,
            "is_admin": False
        },
        {
            "email": "test@example.com",
            "password": "test123", 
            "firstname": "testuser",
            "lastname": "Test User",
            "is_verified": True,
            "is_admin": False
        }
    ]

    
    @property
    def database_url(self) -> str:
        """Construct database URL from individual components."""
        return (
            f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}" # f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            # f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        # return os.getenv("DATABASE_URL")
    
    @property
    def async_database_url(self) -> str:
        """Construct async database URL."""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
    

def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application configuration instance
    """
    return Settings()