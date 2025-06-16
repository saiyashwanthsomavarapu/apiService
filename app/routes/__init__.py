from .user_routes import router as user_router
from .routes import router

__all__ = ["admin_router", "user_router", "router"]