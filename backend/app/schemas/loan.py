from pydantic import BaseModel, ConfigDict

class LoanCreateDTO(BaseModel):
    reader_id: int
    copy_id: int


class LoanDTO(LoanCreateDTO):
    id: int

    model_config = ConfigDict(from_attributes=True)
