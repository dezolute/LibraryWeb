from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class OauthConfig(BaseSettings):
    OAUTH_GOOGLE_CLIENT_SECRET: str
    OAUTH_GOOGLE_CLIENT_ID: str

    @property
    def scopes(self) -> List[str]:
        return oauth_config.OAUTH_SCOPES.split(",")

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra='ignore'
    )

oauth_config = OauthConfig()