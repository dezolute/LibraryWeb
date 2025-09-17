from config.base import BaseConfig


class Settings(BaseConfig):
    PROJECT_NAME: str
    PROJECT_VERSION: str
    DEBUG: bool
    CORS_ALLOWED_ORIGINS: str