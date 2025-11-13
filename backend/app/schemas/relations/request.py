from app.schemas.relations.reader import ReaderSemiRelationDTO, RequestSemiRelationDTO


class RequestRelationDTO(RequestSemiRelationDTO):
    reader: ReaderSemiRelationDTO
