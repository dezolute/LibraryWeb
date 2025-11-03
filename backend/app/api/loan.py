from fastapi import APIRouter

from app.api.types import PaginationType, LoanServiceType, CurrentReaderType
from app.models.types import Role
from app.schemas.loan import LoanCreateDTO
from app.schemas.relations import LoanRelationDTO
from app.utils.errors import Forbidden

loan_router = APIRouter(
    prefix="/loans",
    tags=["Loans"]
)


@loan_router.get("")
async def get_loans(
    pg: PaginationType,
    loan_service: LoanServiceType,
    current_reader: CurrentReaderType
) -> LoanRelationDTO:
    if current_reader == Role.READER:
        raise Forbidden

    db_loans = await loan_service.get_loans(pg=pg)
    return db_loans

@loan_router.post("")
async def create_loan(
    loan: LoanCreateDTO,
    loan_service: LoanServiceType,
    current_reader: CurrentReaderType
):
    if current_reader == Role.READER:
        raise Forbidden

    db_loan = await loan_service.create(loan=loan)
    return db_loan


@loan_router.patch("/{loan_id}")
async def set_loan_returned(
    loan_id: int,
    loan_service: LoanServiceType,
    current_reader: CurrentReaderType
):
    if current_reader == Role.READER:
        raise Forbidden

    db_loan = await loan_service.set_loan_as_returned(loan_id=loan_id)
    return db_loan


@loan_router.get("/overdue")
async def get_overdue_loans(
    pg: PaginationType,
    loan_service: LoanServiceType,
    current_reader: CurrentReaderType
):
    if current_reader.role == Role.READER:
        raise Forbidden

    overdue_loans = await loan_service.get_overdue_loans(pg=pg)
    return overdue_loans
