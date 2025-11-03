from typing import List, Annotated

from pydantic import Field

from app.schemas import ReaderDTO
from app.schemas.profile import ProfileDTO
from app.schemas.relations.loan import LoanRelationDTO
from .request import RequestSemiRelationDTO


class ReaderRelationDTO(ReaderDTO):
    profile: ProfileDTO
    requests: Annotated[list[RequestSemiRelationDTO], Field(default=[])]
    loans: Annotated[list[LoanRelationDTO], Field(default=[])]
