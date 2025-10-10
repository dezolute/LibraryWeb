from pydantic_settings import BaseSettings

class RedisConfig(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    class Config:
        env_file = "../.env"
        ignore_empty = True
        extra = "ignore"

redis_config = RedisConfig()