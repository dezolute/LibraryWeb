from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra='ignore'
    )

redis_config = RedisConfig()