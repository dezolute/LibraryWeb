from .auth import auth_router
from .book import book_router
from .user import user_router

__all__ = ["auth_router", "book_router", "user_router"]
