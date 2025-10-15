from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class PairTokens(BaseModel):
    model_config = ConfigDict(extra='ignore')

    access_token: str
    refresh_token: str
    token_id: str


class TokenData(BaseModel):
    user_id: int | None = None
