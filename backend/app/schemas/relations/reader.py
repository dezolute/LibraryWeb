from typing import Annotated

from pydantic import Field

from app.schemas import ReaderDTO
from app.schemas.profile import ProfileDTO
from app.schemas.relations.semi_loan import LoanSemiRelationDTO
from .request import RequestSemiRelationDTO


class ReaderRelationDTO(ReaderDTO):
    profile: ProfileDTO
    requests: Annotated[list[RequestSemiRelationDTO], Field(default=[])]
    loans: Annotated[list[LoanSemiRelationDTO], Field(default=[])]
