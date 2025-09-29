from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str

    class Config:
        env_file = "../.env"
        env_ignore_empty = True
        extra = "ignore"


auth_config = AuthConfig()
