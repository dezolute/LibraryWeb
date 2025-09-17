from pydantic_settings import BaseSettings


class ConfigDB(BaseSettings):
    POSTGRE_USER: str
    POSTGRE_PASSWORD: str
    POSTGRE_HOST: str
    POSTGRE_PORT: str
    POSTGRE_DB: str
    ECHO: bool

    class Config:
        env_file = ".env"
        env_ignore_empty = True
        extra = "ignore"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRE_USER}:{self.POSTGRE_PASSWORD}@"
            f"{self.POSTGRE_HOST}:{self.POSTGRE_PORT}/{self.POSTGRE_DB}"
        )


db_config = ConfigDB()