from app.schemas import ReaderDTO
from app.schemas.profile import ProfileDTO


class ProfileRelationDTO(ProfileDTO):
    reader: ReaderDTO
