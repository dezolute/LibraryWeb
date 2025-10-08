from typing import List

from pydantic_settings import BaseSettings

class OauthConfig(BaseSettings):
    OAUTH_GOOGLE_CLIENT_SECRET: str
    OAUTH_GOOGLE_CLIENT_ID: str

    @property
    def scopes(self) -> List[str]:
        return oauth_config.OAUTH_SCOPES.split(",")

    class Config:
        env_file = "../.env"
        env_empty_ignore = True
        extra = 'ignore'

oauth_config = OauthConfig()