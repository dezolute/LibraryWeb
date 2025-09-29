from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_VERSION: str
    HOST: str
    PORT: int
    RELOAD: bool
    DEBUG: bool
    CORS_ALLOWED_ORIGINS: str

    @property
    def origins(self) -> list[str]:
        return self.CORS_ALLOWED_ORIGINS.split(",")

    class Config:
        env_file = "../.env"
        env_ignore_empty = True
        extra = "ignore"


settings = Settings()
