from app.schemas import BookDTO, RequestDTO, ReaderDTO


class RequestSemiRelationDTO(RequestDTO):
    book: BookDTO


class RequestRelationDTO(RequestSemiRelationDTO):
    reader: ReaderDTO
