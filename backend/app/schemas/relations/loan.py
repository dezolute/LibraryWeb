from app.schemas.relations.reader import ReaderSemiRelationDTO, LoanSemiRelationDTO

class LoanRelationDTO(LoanSemiRelationDTO):
    reader: ReaderSemiRelationDTO
