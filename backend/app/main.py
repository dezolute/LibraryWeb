from urllib.request import Request

import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.config import settings
from app.router import get_apps_routes
from app.utils.admin.sqladmin import get_admin
from app.utils.cache import lifespan


def get_app() -> FastAPI:
    application = FastAPI(
        title=f"📚 {settings.PROJECT_NAME}",
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
        root_path="/api",
        lifespan=lifespan,
    )

    application.include_router(get_apps_routes())

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = get_app()
admin = get_admin(app)


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse(url="/api/docs")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

    