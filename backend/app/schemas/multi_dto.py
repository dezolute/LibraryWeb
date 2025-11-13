from typing import TypeVar, List

from pydantic import BaseModel, ConfigDict

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class MultiDTO[SchemaType](BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[SchemaType]
    total: int