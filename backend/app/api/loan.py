from typing import Annotated

from fastapi import APIRouter, Query, Depends
from fastapi.responses import FileResponse

from app.api.types import PaginationType, LoanServiceType, CurrentReaderType
from app.models.types import Role
from app.schemas import MultiDTO
from app.schemas.relations import LoanRelationDTO
from app.schemas.utils.filters import LoanFilter
from app.utils.errors import Forbidden
from app.schemas.loan import LoanDTO

loan_router = APIRouter(
    prefix="/loans",
    tags=["Loans"]
)


@loan_router.get("")
async def get_loans(
    pg: PaginationType,
    filters: Annotated[LoanFilter, Depends(LoanFilter)],
    loan_service: LoanServiceType,
    current_reader: CurrentReaderType
) -> MultiDTO[LoanRelationDTO]:
    if current_reader == Role.READER:
        raise Forbidden

    db_loans = await loan_service.get_loans(
        pg=pg,
        conditions=filters.conditions
    )
    return db_loans

@loan_router.patch("/{loan_id}")
async def set_loan_returned(
    loan_id: int,
    loan_service: LoanServiceType,
    current_reader: CurrentReaderType
) -> LoanDTO:
    if current_reader == Role.READER:
        raise Forbidden

    db_loan = await loan_service.set_loan_as_returned(loan_id=loan_id)
    return db_loan


@loan_router.get("/overdue")
async def get_overdue_loans(
    pg: PaginationType,
    loan_service: LoanServiceType,
    current_reader: CurrentReaderType
) -> MultiDTO[LoanRelationDTO]:
    if current_reader.role == Role.READER:
        raise Forbidden

    overdue_loans = await loan_service.get_overdue_loans(pg=pg)
    return overdue_loans


@loan_router.get("/overdue/report")
async def get_overdue_report(
    pg: PaginationType,
    current_reader: CurrentReaderType,
    loan_service: LoanServiceType,
) -> FileResponse:
    if current_reader.role == Role.READER:
        raise Forbidden

    loan_report = await loan_service.overdue_report(pg=pg)
    return loan_report