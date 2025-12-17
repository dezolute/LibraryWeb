from typing import Annotated

from fastapi import APIRouter, Query, UploadFile, Request
from starlette import status
from starlette.responses import RedirectResponse

from app.api.types import ReaderServiceType, CurrentReaderType, RequestServiceType
from app.schemas import ReaderCreateDTO, RequestDTO
from app.schemas.relations import ReaderRelationDTO, RequestSemiRelationDTO, ReaderSemiRelationDTO

reader_router = APIRouter(prefix="/readers", tags=["Readers"])


@reader_router.post("")
async def create_reader(
        reader: ReaderCreateDTO,
        reader_service: ReaderServiceType,
) -> ReaderSemiRelationDTO:
    db_reader = await reader_service.add_reader(reader)
    return db_reader


@reader_router.get("/me")
async def get_current_reader(
        current_reader: CurrentReaderType,
) -> ReaderRelationDTO:
    return current_reader


@reader_router.patch("/me/icon")
async def set_reader_avatar(
        icon: UploadFile,
        current_reader: CurrentReaderType,
        reader_service: ReaderServiceType,
) -> ReaderRelationDTO:
    updated_reader = await reader_service.set_icon_to_reader(current_reader.id, icon)
    return updated_reader


@reader_router.post("/me/requests")
async def make_requests(
        book_id: int,
        current_reader: CurrentReaderType,
        request_service: RequestServiceType,
) -> RequestDTO:
    requests = await request_service.create_request(
        reader_id=current_reader.id,
        book_id=book_id,
    )
    return requests


@reader_router.delete("/me/requests/{request_id}")
async def remove_request(
        request_id: int,
        current_reader: CurrentReaderType,
        request_service: RequestServiceType,
) -> RequestDTO:
    request = await request_service.reader_remove_request(request_id, current_reader.id)
    return request


@reader_router.get("/verify")
async def get_reader_verification(
        req: Request,
        token: Annotated[str, Query()],
        reader_service: ReaderServiceType,
):
    await reader_service.set_verify_email_to_reader(token)
    return RedirectResponse(
        f"http://{req.headers.get("host")}/login",
        status_code=status.HTTP_302_FOUND
    )
