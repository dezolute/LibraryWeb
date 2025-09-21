import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from router import get_apps_routes

def get_app() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
    )

    application.include_router(get_apps_routes())

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=True,
        allow_methods=["*"],
    )

    return application


app = get_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
    )
