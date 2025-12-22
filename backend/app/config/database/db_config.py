from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigDB(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    SSL: bool = False
    ECHO: bool

    @property
    def database_url(self) -> str:
        if self.SSL:
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}?sslmode=require"
            )
        else:
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra='ignore'
    )


db_config = ConfigDB()
