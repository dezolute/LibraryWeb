from .admin import admin_router
from .auth import auth_router
from .book import book_router
from .request import request_router
from .user import user_router

__all__ = [
    "auth_router",
    "book_router",
    "user_router",
    "request_router",
    "admin_router",
]
