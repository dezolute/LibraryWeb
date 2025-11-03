from datetime import  date

from app.services.request import RequestService
from app.services.book import BookService
from app.services.reader import ReaderService
from app.repositories import RepositoryType
from app.models import RequestORM, LoanORM
from app.models.types import BookCopyStatus, RequestStatus
from app.schemas import MultiDTO
from app.schemas.loan import LoanCreateDTO
from app.schemas.relations import LoanRelationDTO
from app.schemas.utils import Pagination


class LoanService:
    def __init__(
            self,
            loan_repository: RepositoryType,
            book_service: BookService,
            reader_service: ReaderService,
            request_service: RequestService,
    ):
        self.loan_repository: RepositoryType = loan_repository
        self.book_service: BookService = book_service
        self.reader_service: ReaderService = reader_service
        self.request_service: RequestService = request_service

    async def get_loans(self, pg: Pagination) -> MultiDTO[LoanRelationDTO]:
        loans, total = await self.loan_repository.find_all(pg=pg)

        return MultiDTO(
            items=[LoanRelationDTO.model_validate(loan) for loan in loans],
            total=total,
        )

    async def create_loan(self, loan: LoanCreateDTO) -> LoanRelationDTO:
        loan_data = loan.model_dump()

        db_loan = await self.loan_repository.create(loan_data)
        copy = await self.book_service.change_copy_status(
            new_status=BookCopyStatus.BORROWED,
            serial_num=loan.serial_num
        )

        requests = await self.request_service.get_multi(
            pg=Pagination(),
            conditions=[
                RequestORM.status != RequestStatus.FULFILLED,
            ],
            book_id=copy.book_id
        )
        await self.request_service.update_status(request_id=requests[0].id, new_status=RequestStatus.FULFILLED)

        db_loan.copy = copy

        return LoanRelationDTO.model_validate(db_loan)

    async def set_loan_as_returned(self, loan_id) -> LoanRelationDTO:
        await self.loan_repository.update(data={ "return_date": date.today() }, id=loan_id)
        loan = await self.loan_repository.find(id=loan_id)

        copy = await self.book_service.change_copy_status(
            new_status=BookCopyStatus.AVAILABLE,
            serial_num=loan.copy.serial_num
        )
        loan.copy = copy

        return LoanRelationDTO.model_validate(loan)

    async def get_overdue_loans(self, pg: Pagination) -> MultiDTO[LoanRelationDTO]:
        loans, total = await self.loan_repository.find_all(
            pg=pg,
            conditions=[
                LoanORM.due_date >= date.today(),
            ]
        )

        return MultiDTO(
            items=[
                LoanRelationDTO.model_validate(loan)
                for loan in loans
            ],
        total=total,
        )