from fastapi import APIRouter

from app.api import (
    auth_router,
    user_router,
    book_router,
    request_router,
    admin_router,
)


def get_apps_routes() -> APIRouter:
    router = APIRouter()

    router.include_router(auth_router)
    router.include_router(user_router)
    router.include_router(book_router)
    router.include_router(request_router)
    router.include_router(admin_router)

    return router
