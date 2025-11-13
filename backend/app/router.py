from fastapi import APIRouter

from app.api import (
    auth_router,
    reader_router,
    book_router,
    request_router, loan_router,
)


def get_apps_routes() -> APIRouter:
    router = APIRouter()

    router.include_router(auth_router)
    router.include_router(reader_router)
    router.include_router(book_router)
    router.include_router(request_router)
    router.include_router(loan_router)

    return router
