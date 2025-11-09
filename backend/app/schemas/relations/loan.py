from app.schemas.relations.reader import ReaderRelationDTO
from app.schemas.relations.semi_loan import LoanSemiRelationDTO


class LoanRelationDTO(LoanSemiRelationDTO):
    reader: ReaderRelationDTO
