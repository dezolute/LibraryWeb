from typing import Generic, TypeVar, List

from pydantic import BaseModel, ConfigDict

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class MultiDTO(BaseModel, Generic[SchemaType]):
    items: List[SchemaType]
    total: int

    model_config = ConfigDict(from_attributes=True)
