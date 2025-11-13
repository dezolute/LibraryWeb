from pydantic import BaseModel, ConfigDict

class ProfileCreateDTO(BaseModel):
    reader_id: int
    full_name: str

class ProfileDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str
    avatar_url: str | None = None