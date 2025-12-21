from fastapi import FastAPI
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.config import auth_config
from app.config.database import db
from app.models.types import Role
from app.repositories import RepositoryFactory as RF
from app.utils import OAuth2Utility
from app.utils.admin.views import (
    BookAdmin,
    BookCopyAdmin,
    LoanAdmin,
    ProfileAdmin,
    ReaderAdmin,
    RequestAdmin
)


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str) -> None:
        self.reader_repository = RF.reader_repository()
        super().__init__(secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email: str = form.get("username") # type: ignore
        password: str = form.get("password") # type: ignore

        db_reader = await self.reader_repository.find(email=email)
        if not db_reader:
            return False
        if db_reader.role != Role.ADMIN:
            return False

        try:
            return OAuth2Utility.verify_password(password, db_reader.encrypted_password)
        finally:
            request.session.update({
                "access_token": OAuth2Utility.get_tokens({
                    'sub': db_reader.email,
                    'full_name': db_reader.profile.full_name,
                }).access_token,
            })

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("access_token")

        if not token:
            return False

        return True

def get_admin(app: FastAPI) -> Admin:
    backend_auth = AdminAuth(auth_config.JWT_SECRET)

    admin = Admin(
        app=app,
        engine=db.engine,
        session_maker=db.session_factory,
        authentication_backend=backend_auth,
        favicon_url="/LibraryWeb.svg",
    )

    admin.add_view(ReaderAdmin)
    admin.add_view(ProfileAdmin)
    admin.add_view(BookAdmin)
    admin.add_view(BookCopyAdmin)
    admin.add_view(RequestAdmin)
    admin.add_view(LoanAdmin)

    return admin