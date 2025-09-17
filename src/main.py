import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import get_apps_routes
from database.db_config import db_config


print(db_config)

def get_app() -> FastAPI:
    application = FastAPI(
        title="FastAPI",
        version="0.1.0",
        debug=True,
    )

    application.include_router(get_apps_routes())

    application.add_middleware(
        CORSMiddleware,
    )

    return application


app = get_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
    )