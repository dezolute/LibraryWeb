import asyncio
import os
import secrets

from fastapi import UploadFile, HTTPException
from starlette import status

from app.modules import RedisRepository
from app.modules.email import send_verify_email
from app.modules.s3 import upload_file_to_s3
from app.schemas import ReaderDTO, ReaderCreateDTO, ReaderUpdateDTO
from app.schemas.relations import ReaderRelationDTO, ReaderSemiRelationDTO
from app.repositories.sqlalchemy import SqlAlchemyRepository
from app.utils import OAuth2Utility
from app.models.profile import ProfileORM
from app.models.reader import ReaderORM


class ReaderService:
    def __init__(
            self,
            reader_repository: SqlAlchemyRepository[ReaderORM],
            profile_repository: SqlAlchemyRepository[ProfileORM],
    ):
        self.reader_repository: SqlAlchemyRepository[ReaderORM] = reader_repository
        self.profile_repository: SqlAlchemyRepository[ProfileORM] = profile_repository
        self.redis: RedisRepository = RedisRepository()

    async def add_reader(self, reader: ReaderCreateDTO) -> ReaderSemiRelationDTO:
        reader_dict = reader.model_dump()

        clear_reader = ReaderUpdateDTO.model_validate(reader_dict)
        reader_dict = clear_reader.model_dump()

        encrypted_password = OAuth2Utility.get_hashed_password(reader.password)
        reader_dict.update({"encrypted_password": encrypted_password})

        from sqlalchemy import exc
        try:
            full_name = reader_dict.pop("full_name")
            db_reader = await self.reader_repository.create(data=reader_dict)
            print(f"\n\n{db_reader.id}\n\n")
            profile = await self.profile_repository.create(data={
                "full_name": full_name,
                "reader_id": db_reader.id
            })
            db_reader.profile = profile
        except exc.IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )

        token = secrets.token_urlsafe(15)

        _ = await asyncio.create_task(
            send_verify_email(
                str(db_reader.email),
                token,
        ))
        await asyncio.create_task(
            self.redis.set_verify_tokens(
                token,
                db_reader.email
        ))

        return ReaderSemiRelationDTO.model_validate(db_reader)


    async def set_icon_to_reader(self, reader_id: int, file: UploadFile):
        ext = os.path.splitext(file.filename)[-1] # type: ignore
        path_to_file = os.path.join(os.path.abspath("."), "temp", f"new_icon{ext}")

        with open(path_to_file, 'wb') as f:
            f.write(await file.read())

        url = upload_file_to_s3(path_to_file)

        os.remove(path_to_file)

        await self.profile_repository.update(data={"avatar_url": url}, reader_id=reader_id)
        reader = await self.reader_repository.find(id=reader_id)

        book_db = ReaderRelationDTO.model_validate(reader)
        return book_db

    async def get_orm_data(self, **kwargs):
        reader = await self.reader_repository.find(**kwargs)

        if reader is None:
            raise HTTPException(status_code=404)

        return reader

    async def set_verify_email_to_reader(self, token: str) -> ReaderDTO:
        redis_email = await self.redis.get_verify_tokens(token)
        if not redis_email:
            raise HTTPException(status_code=404, detail="Email not found")

        await self.redis.delete_verify_tokens(token)

        verified_reader = await self.reader_repository.update(data={"verified": True}, email=redis_email)
        return ReaderDTO.model_validate(verified_reader)
